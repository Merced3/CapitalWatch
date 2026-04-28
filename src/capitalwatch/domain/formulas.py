from capitalwatch.domain.models import FinancialInputs, MagicFormulaResult


def calculate_magic_formula(financials):
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
