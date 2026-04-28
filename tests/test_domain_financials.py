import unittest

from capitalwatch.domain.financial_mapping import (
    MissingFinancialStatement,
    map_massive_financials_response,
)
from capitalwatch.domain.formulas import calculate_magic_formula
from capitalwatch.domain.models import FinancialInputs


def sample_massive_response(balance_sheet_overrides=None):
    balance_sheet = {
        "assets": {"value": 1000},
        "liabilities": {"value": 300},
        "current_assets": {"value": 400},
        "current_liabilities": {"value": 150},
        "cash_and_cash_equivalents": {"value": 50},
        "long_term_debt": {"value": 200},
    }
    balance_sheet.update(balance_sheet_overrides or {})

    return {
        "results": [
            {
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "financials": {
                    "balance_sheet": balance_sheet,
                    "income_statement": {
                        "operating_income_loss": {"value": 100},
                    },
                },
            }
        ]
    }


class FinancialMappingTests(unittest.TestCase):
    def test_maps_massive_response_to_financial_inputs(self):
        financials = map_massive_financials_response(
            ticker="ANF",
            data=sample_massive_response(),
            market_cap=2000,
            market_cap_accuracy="accurate",
        )

        self.assertEqual(financials.ticker, "ANF")
        self.assertEqual(financials.ebit, 100)
        self.assertEqual(financials.cash, 50)
        self.assertEqual(financials.debt, 200)
        self.assertEqual(financials.market_cap, 2000)
        self.assertEqual(financials.accuracies["cash"], "accurate")
        self.assertEqual(financials.accuracies["debt"], "accurate")

    def test_missing_income_statement_raises_mapping_error_with_snapshot_accuracy(self):
        data = {
            "results": [
                {
                    "start_date": "2025-01-01",
                    "end_date": "2025-12-31",
                    "financials": {"balance_sheet": {}},
                }
            ]
        }

        with self.assertRaises(MissingFinancialStatement) as error:
            map_massive_financials_response(
                ticker="ANF",
                data=data,
                market_cap=2000,
                market_cap_accuracy="accurate",
            )

        self.assertEqual(error.exception.accuracies, {"error": "missing_income_statement"})


class FormulaTests(unittest.TestCase):
    def test_calculates_magic_formula_from_clean_financial_inputs(self):
        result = calculate_magic_formula(
            FinancialInputs(
                ticker="ANF",
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
        )

        self.assertEqual(result.ticker, "ANF")
        self.assertEqual(result.earnings_yield, 4.65)
        self.assertEqual(result.roc, 10.53)
        self.assertEqual(result.accuracy, "accurate")


if __name__ == "__main__":
    unittest.main()
