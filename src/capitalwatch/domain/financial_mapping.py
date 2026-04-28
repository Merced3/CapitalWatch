from capitalwatch.domain.financial_statement_fields import estimate_cash, estimate_debt, get_best_field
from capitalwatch.domain.models import FinancialInputs


class MissingFinancialStatement(Exception):
    def __init__(self, message, accuracies):
        super().__init__(message)
        self.accuracies = accuracies


def map_massive_financials_response(
    ticker,
    data,
    market_cap,
    market_cap_accuracy,
):
    if "results" not in data or not data["results"]:
        raise Exception("No data found")

    financial_data = data["results"][0]
    if "financials" not in financial_data or "income_statement" not in financial_data["financials"]:
        raise MissingFinancialStatement(
            "Missing 'income_statement'",
            {"error": "missing_income_statement"},
        )

    fin = financial_data["financials"]
    balance_sheet = fin["balance_sheet"]
    income_statement = fin["income_statement"]

    ebit, ebit_accuracy = get_best_field(income_statement, "operating_income_loss")
    assets, assets_accuracy = get_best_field(balance_sheet, "assets")
    liabilities, liabilities_accuracy = get_best_field(balance_sheet, "liabilities")
    current_assets, current_assets_accuracy = get_best_field(balance_sheet, "current_assets")
    current_liabilities, current_liabilities_accuracy = get_best_field(
        balance_sheet,
        "current_liabilities",
    )
    cash, cash_accuracy = estimate_cash(balance_sheet)
    debt, debt_accuracy = estimate_debt(balance_sheet)

    accuracies = {
        "ebit": ebit_accuracy,
        "assets": assets_accuracy,
        "liabilities": liabilities_accuracy,
        "current_assets": current_assets_accuracy,
        "current_liabilities": current_liabilities_accuracy,
        "cash": cash_accuracy,
        "debt": debt_accuracy,
        "market_cap": market_cap_accuracy,
    }

    return FinancialInputs(
        ticker=ticker,
        ebit=ebit,
        assets=assets,
        liabilities=liabilities,
        current_assets=current_assets,
        current_liabilities=current_liabilities,
        cash=cash,
        debt=debt,
        market_cap=market_cap,
        accuracies=accuracies,
        start_date=financial_data["start_date"],
        end_date=financial_data["end_date"],
    )
