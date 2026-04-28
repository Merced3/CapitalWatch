from capitalwatch.clients.massive_client import MassiveClient
from capitalwatch.domain.financial_mapping import (
    MissingFinancialStatement,
    map_massive_financials_response,
)
from capitalwatch.domain.formulas import calculate_magic_formula
from capitalwatch.domain.models import RawCompanyDataSnapshot


class FinancialsService:
    def __init__(self, client=None, cache=None):
        self.client = client or MassiveClient()
        self.cache = cache

    def fetch_financials(self, ticker):
        data = self.client.fetch_financials(ticker)
        shares_outstanding = self.client.fetch_shares_outstanding(ticker)

        market_cap, market_cap_accuracy = self._fetch_market_cap(ticker, shares_outstanding)
        try:
            financials = map_massive_financials_response(
                ticker=ticker,
                data=data,
                market_cap=market_cap,
                market_cap_accuracy=market_cap_accuracy,
            )
        except MissingFinancialStatement as exc:
            self._save_snapshot(
                ticker,
                data,
                shares_outstanding,
                exc.accuracies,
                partial=True,
            )
            raise Exception(str(exc))

        self._save_snapshot(ticker, data, shares_outstanding, financials.accuracies)

        return financials

    def calculate_magic_formula(self, financials):
        return calculate_magic_formula(financials)

    def _fetch_market_cap(self, ticker, shares_outstanding):
        try:
            response = self.client.fetch_previous_close(ticker)

            if "results" not in response or not response["results"]:
                raise Exception(f"Couldn't fetch price for {ticker}")

            close_price = response["results"][0]["c"]

            if not shares_outstanding:
                raise Exception(f"Shares outstanding not provided for {ticker}")

            return close_price * shares_outstanding, "accurate"
        except Exception:
            return 0, "rough"

    def _save_snapshot(self, ticker, data, shares_outstanding, accuracies, partial=False):
        if self.cache is None:
            return

        snapshot = RawCompanyDataSnapshot(
            ticker=ticker,
            shares_outstanding=shares_outstanding,
            accuracies=accuracies,
            raw_api_data=data,
        )
        self.cache.save_snapshot(snapshot, partial=partial)
