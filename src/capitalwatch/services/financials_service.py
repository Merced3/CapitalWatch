from capitalwatch.clients.massive_client import MassiveClient
from capitalwatch.domain.models import (
    FinancialInputs,
    MagicFormulaResult,
    RawCompanyDataSnapshot,
)


class FinancialsService:
    def __init__(self, client=None, cache=None):
        self.client = client or MassiveClient()
        self.cache = cache

    def fetch_financials(self, ticker):
        data = self.client.fetch_financials(ticker)
        shares_outstanding = self.client.fetch_shares_outstanding(ticker)

        if "results" not in data or not data["results"]:
            raise Exception("No data found")

        financial_data = data["results"][0]
        if "financials" not in financial_data or "income_statement" not in financial_data["financials"]:
            self._save_snapshot(
                ticker,
                data,
                shares_outstanding,
                {"error": "missing_income_statement"},
                partial=True,
            )
            raise Exception("Missing 'income_statement'")

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
        market_cap, market_cap_accuracy = self._fetch_market_cap(ticker, shares_outstanding)

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

        self._save_snapshot(ticker, data, shares_outstanding, accuracies)

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

    def calculate_magic_formula(self, financials):
        if isinstance(financials, dict):
            financials = FinancialInputs(**financials)

        if not financials.market_cap:
            raise Exception(f"Missing market cap for {financials.ticker}")

        enterprise_value = financials.market_cap + financials.debt - financials.cash
        earnings_yield = financials.ebit / enterprise_value if enterprise_value else 0

        working_capital = financials.current_assets - financials.current_liabilities
        net_fixed_assets = financials.assets - financials.liabilities
        capital = working_capital + net_fixed_assets
        roc = financials.ebit / capital if capital else 0

        # Preserve the legacy rollup semantics exactly, including the literal
        # "estimated" membership check.
        accuracy_values = list(financials.accuracies.values())
        if "rough" in accuracy_values:
            calc_accuracy = "rough"
        elif "estimated" in accuracy_values:
            calc_accuracy = "estimated"
        else:
            calc_accuracy = "accurate"

        return MagicFormulaResult(
            ticker=financials.ticker,
            earnings_yield=round(earnings_yield * 100, 2),
            roc=round(roc * 100, 2),
            accuracy=calc_accuracy,
        )

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


def estimate_cash(balance_sheet):
    accurate_cash_fields = [
        "cash",
        "cash_and_cash_equivalents",
        "cash_and_short_term_investments",
        "other_current_assets",
    ]
    for field in accurate_cash_fields:
        if field in balance_sheet and "value" in balance_sheet[field]:
            value = balance_sheet[field]["value"]
            if value == 0:
                return 0, "accurate"
            return value, "accurate"

    estimation_rules = [
        ("current_assets", ["inventory"]),
    ]

    for base_field, subtract_fields in estimation_rules:
        if base_field in balance_sheet and "value" in balance_sheet[base_field]:
            base_value = balance_sheet[base_field]["value"]
            subtract_total = 0

            for subtract_field in subtract_fields:
                if subtract_field in balance_sheet and "value" in balance_sheet[subtract_field]:
                    subtract_total += balance_sheet[subtract_field]["value"]

            return base_value - subtract_total, "estimated"

    return 0, "rough"


def estimate_debt(balance_sheet):
    accurate_debt_fields = ["total_debt", "long_term_debt"]
    for field in accurate_debt_fields:
        if field in balance_sheet and "value" in balance_sheet[field]:
            value = balance_sheet[field]["value"]
            if value == 0:
                return 0, "accurate"
            return value, "accurate"

    if "noncurrent_liabilities" in balance_sheet and "value" in balance_sheet["noncurrent_liabilities"]:
        return balance_sheet["noncurrent_liabilities"]["value"], "estimated_strong"

    if "current_liabilities" in balance_sheet and "value" in balance_sheet["current_liabilities"]:
        return balance_sheet["current_liabilities"]["value"], "estimated_weak"
    if "accounts_payable" in balance_sheet and "value" in balance_sheet["accounts_payable"]:
        return balance_sheet["accounts_payable"]["value"], "estimated_weak"

    return 0, "rough"


def get_best_field(source, keys_or_single):
    keys = keys_or_single if isinstance(keys_or_single, list) else [keys_or_single]
    for key in keys:
        if key in source and "value" in source[key]:
            return source[key]["value"], "accurate"
    return 0, "rough"
