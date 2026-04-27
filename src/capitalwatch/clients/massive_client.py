import requests
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from capitalwatch import config


class MassiveClient:
    """HTTP adapter for Massive-compatible market data endpoints.

    The current request flow still uses the existing Polygon-hosted API URLs
    because that is what the legacy project already depends on.
    """

    def __init__(self, api_key=None, financials_url=None, session=None):
        self.api_key = api_key or config.get_massive_api_key()
        self.financials_url = financials_url or config.get_massive_financials_url()
        self.session = session or requests.Session()

    def fetch_financials(self, ticker):
        url = f"{self.financials_url}?ticker={ticker}&limit=1&apiKey={self.api_key}"
        return self._get_json(url)

    def fetch_previous_close(self, ticker):
        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
            f"?adjusted=true&apiKey={self.api_key}"
        )
        return self._get_json(url)

    def fetch_ticker_reference(self, ticker):
        url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={self.api_key}"
        return self._get_json(url)

    def fetch_reference_tickers(self, params=None, next_url=None):
        if next_url is not None:
            return self._get_json(self._append_api_key(next_url))

        url = "https://api.polygon.io/v3/reference/tickers"
        return self._get_json(url, params=self._with_api_key(params))

    def fetch_shares_outstanding(self, ticker):
        response = self.fetch_ticker_reference(ticker)

        try:
            return float(response["results"]["share_class_shares_outstanding"])
        except (KeyError, TypeError):
            raise Exception(f"Could not fetch shares outstanding for {ticker}")

    def _get_json(self, url, params=None):
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _append_api_key(self, url):
        parsed = urlparse(url)
        query_items = parse_qsl(parsed.query, keep_blank_values=True)

        if not any(key == "apiKey" for key, _ in query_items):
            query_items.append(("apiKey", self.api_key))

        return urlunparse(parsed._replace(query=urlencode(query_items)))

    def _with_api_key(self, params):
        request_params = dict(params or {})
        request_params.setdefault("apiKey", self.api_key)
        return request_params
