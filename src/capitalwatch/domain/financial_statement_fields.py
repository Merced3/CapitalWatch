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
