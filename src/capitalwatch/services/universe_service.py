from pathlib import Path

from capitalwatch import config
from capitalwatch.clients.massive_client import MassiveClient


class FileTickerSource:
    """Temporary text-file ticker source until universe acquisition is replaced."""

    def __init__(self, path=None):
        self.path = Path(path) if path is not None else config.DEFAULT_TICKER_FILE

    def load_tickers(self):
        with self.path.open("r", encoding="utf-8") as handle:
            return normalize_tickers(handle)


class MassiveActiveTickerSource:
    """Massive-backed ticker source for the active stock universe."""

    def __init__(self, client=None, locale="us", market="stocks", type_code=None):
        self.client = client or MassiveClient()
        self.locale = locale
        self.market = market
        self.type_code = type_code

    def load_tickers(self):
        return list(self.iter_tickers())

    def iter_tickers(self):
        for result in self.iter_ticker_records():
            ticker = result.get("ticker")
            if not ticker:
                continue

            normalized = ticker.strip().upper()
            if normalized:
                yield normalized

    def load_ticker_records(self):
        return list(self.iter_ticker_records())

    def iter_ticker_records(self):
        params = {
            "locale": self.locale,
            "market": self.market,
            "active": "true",
            "limit": 1000,
            "sort": "ticker",
            "order": "asc",
        }
        if self.type_code:
            params["type"] = self.type_code

        next_url = None
        page_number = 0

        while True:
            page_number += 1
            response = self.client.fetch_reference_tickers(
                params=params if next_url is None else None,
                next_url=next_url,
            )

            self._validate_reference_ticker_response(response, page_number=page_number)

            for record in response["results"]:
                yield record

            next_url = response.get("next_url")

            if not next_url:
                break

    def _validate_reference_ticker_response(self, response, page_number):
        status = response.get("status")
        error = response.get("error")

        if error:
            raise RuntimeError(f"Massive universe request failed on page {page_number}: {error}")

        if status and status != "OK":
            raise RuntimeError(
                f"Massive universe request returned status {status!r} on page {page_number}."
            )

        if "results" not in response:
            raise RuntimeError(
                "Massive universe request returned no results field on "
                f"page {page_number}. Response keys: {sorted(response.keys())}"
            )


def normalize_tickers(tickers):
    return [ticker.strip().upper() for ticker in tickers if ticker.strip()]


def load_tickers(source=None):
    if source is None:
        return FileTickerSource().load_tickers()

    if isinstance(source, (str, Path)):
        return FileTickerSource(source).load_tickers()

    if hasattr(source, "load_tickers"):
        return normalize_tickers(source.load_tickers())

    return normalize_tickers(source)
