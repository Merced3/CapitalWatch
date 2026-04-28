import unittest

from capitalwatch.domain.models import FinancialInputs, MagicFormulaResult
from capitalwatch.services.scan_service import ScanService


class StubFinancialsService:
    def fetch_financials(self, ticker):
        if ticker == "BAD":
            raise Exception("No data found")

        return FinancialInputs(
            ticker=ticker,
            ebit=100,
            assets=1000,
            liabilities=300,
            current_assets=400,
            current_liabilities=150,
            cash=50,
            debt=200,
            market_cap=2000,
            accuracies={"ebit": "accurate"},
            start_date="2025-01-01",
            end_date="2025-12-31",
        )

    def calculate_magic_formula(self, financials):
        return MagicFormulaResult(
            ticker=financials.ticker,
            earnings_yield=4.65,
            roc=10.53,
            accuracy="accurate",
        )


class ScanServiceTests(unittest.TestCase):
    def test_run_groups_successes_and_captures_errors_without_printing(self):
        report = ScanService(financials_service=StubFinancialsService()).run(
            tickers=["ANF", "BAD"]
        )

        period = ("2025-01-01", "2025-12-31")
        self.assertEqual(len(report.entries_by_period[period]), 1)
        self.assertEqual(report.ranked_results[0].ticker, "ANF")
        self.assertEqual(report.errors[0].ticker, "BAD")
        self.assertEqual(str(report.errors[0].error), "No data found")


if __name__ == "__main__":
    unittest.main()
