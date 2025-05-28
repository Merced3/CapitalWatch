# utils.py

import os
import json
import requests
from config import POLYGON_API_KEY, BASE_URL

def fetch_financials(ticker):
    url = f"{BASE_URL}?ticker={ticker}&limit=1&apiKey={POLYGON_API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    
    shares_outstanding = fetch_shares_outstanding(ticker)
    
    if "results" not in data or not data["results"]:
        raise Exception(f"No data found")

    financial_data = data["results"][0]
    if "financials" not in financial_data or "income_statement" not in financial_data["financials"]:
        save_financial_snapshot(ticker, data, shares_outstanding, {"error": "missing_income_statement"}, folder="company_data/partial")
        raise Exception(f"Missing 'income_statement'")

    fin = financial_data["financials"]
    bs = fin["balance_sheet"]
    is_ = fin["income_statement"]

    ebit, ebit_accuracy = get_best_field(is_, "operating_income_loss")
    assets, assets_accuracy = get_best_field(bs, "assets")
    lbts, lbts_accuracy = get_best_field(bs, "liabilities")
    ca, ca_accuracy = get_best_field(bs, "current_assets")
    cl, cl_accuracy = get_best_field(bs, "current_liabilities")
    cash, cash_accuracy = estimate_cash(bs)
    debt, debt_accuracy = estimate_debt(bs)
    mc, mc_accuracy = fetch_market_cap(ticker, shares_outstanding)

    accuracies = {
        "ebit": ebit_accuracy,
        "assets": assets_accuracy,
        "liabilities": lbts_accuracy,
        "current_assets": ca_accuracy,
        "current_liabilities": cl_accuracy,
        "cash": cash_accuracy,
        "debt": debt_accuracy,
        "market_cap": mc_accuracy
    }

    save_financial_snapshot(ticker, data, shares_outstanding, accuracies)

    # Near the bottom of fetch_financials()
    start_date = data["results"][0]["start_date"]
    end_date = data["results"][0]["end_date"]

    return {
        "ticker": ticker,
        "ebit": ebit,
        "assets": assets,
        "liabilities": lbts,
        "current_assets": ca,
        "current_liabilities": cl,
        "cash": cash,
        "debt": debt,
        "market_cap": mc,
        "accuracies": accuracies,
        "start_date": start_date,
        "end_date": end_date
    }

def calculate_magic_formula(financials):
    ebit = financials["ebit"]
    cash = financials["cash"]
    debt = financials["debt"]
    mc = financials["market_cap"]
    current_assets = financials["current_assets"]
    current_liabilities = financials["current_liabilities"]
    assets = financials["assets"]
    liabilities = financials["liabilities"]
    accuracies = financials["accuracies"]

    if not mc:
        raise Exception(f"Missing market cap for {financials['ticker']}")

    ev = mc + debt - cash
    earnings_yield = ebit / ev if ev else 0

    working_capital = current_assets - current_liabilities
    net_fixed_assets = assets - liabilities  # rough approximation
    capital = working_capital + net_fixed_assets
    roc = ebit / capital if capital else 0

    accs = list(accuracies.values())
    if "rough" in accs:
        calc_accuracy = "rough"
    elif "estimated" in accs:
        calc_accuracy = "estimated"
    else:
        calc_accuracy = "accurate"

    return {
        "ticker": financials["ticker"],
        "earnings_yield": round(earnings_yield * 100, 2),
        "roc": round(roc * 100, 2),
        "accuracy": calc_accuracy
    }

def estimate_cash(bs):
    # ✅ Accurate direct fields
    acc_cash_fields = [
        "cash",
        "cash_and_cash_equivalents",
        "cash_and_short_term_investments",
        "other_current_assets" # Often includes cash-like items if not explicitly separated
    ]
    for field in acc_cash_fields:
        if field in bs and "value" in bs[field]:
            value = bs[field]["value"]
            if value == 0:
                return 0, "accurate"  # Cash exists and is zero by report
            return value, "accurate"
    
    # 🧠 Estimated logic: subtract unwanted parts from a base value
    # Format: ("base_field", ["subtract_field_1", "subtract_field_2", ...])
    estimation_rules = [
        ("current_assets", ["inventory"]),  # Can add more later
    ]

    for base_field, subtract_fields in estimation_rules:
        if base_field in bs and "value" in bs[base_field]:
            base_value = bs[base_field]["value"]
            subtract_total = 0

            for sf in subtract_fields:
                if sf in bs and "value" in bs[sf]:
                    subtract_total += bs[sf]["value"]

            return base_value - subtract_total, "estimated"

    # ❌ If no usable fields found
    return 0, "rough"

def estimate_debt(bs):
    # Accurate: clear debt fields
    acc_debt_fields = ["total_debt", "long_term_debt"]
    for field in acc_debt_fields:
        if field in bs and "value" in bs[field]:
            value = bs[field]["value"]
            if value == 0:
                return 0, "accurate"  # Explicitly stated: no debt
            return value, "accurate"

    # Strong estimate: trustworthy substitutes
    if "noncurrent_liabilities" in bs and "value" in bs["noncurrent_liabilities"]:
        return bs["noncurrent_liabilities"]["value"], "estimated_strong"

    # Weak estimate: lower reliability
    if "current_liabilities" in bs and "value" in bs["current_liabilities"]:
        return bs["current_liabilities"]["value"], "estimated_weak"
    if "accounts_payable" in bs and "value" in bs["accounts_payable"]:
        return bs["accounts_payable"]["value"], "estimated_weak"

    # If nothing is available, we don't know
    return 0, "rough"

def get_best_field(source, keys_or_single, label=None):
    keys = keys_or_single if isinstance(keys_or_single, list) else [keys_or_single]
    for key in keys:
        if key in source and "value" in source[key]:
            return source[key]["value"], "accurate"
    return 0, "rough"

def fetch_market_cap(ticker, shares_outstanding):
    try:
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={POLYGON_API_KEY}"
        resp = requests.get(url).json()

        if "results" not in resp or not resp["results"]:
            raise Exception(f"Couldn't fetch price for {ticker}")

        close_price = resp["results"][0]["c"]

        if not shares_outstanding:
            raise Exception(f"Shares outstanding not provided for {ticker}")
        mc_accuracy = "accurate"
        market_cap = close_price * shares_outstanding
    except:
        market_cap = 0
        mc_accuracy = "rough"
    return market_cap, mc_accuracy

def load_tickers(filepath="tickers.txt"):
    with open(filepath, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

def save_financial_snapshot(ticker, data, shares_outstanding, accuracies, folder="company_data"):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{ticker}_financials.json")

    snapshot = {
        "ticker": ticker,
        "shares_outstanding": shares_outstanding,
        "accuracies": accuracies,
        "raw_api_data": data
    }

    with open(filepath, "w") as f:
        json.dump(snapshot, f, indent=4)

def fetch_shares_outstanding(ticker):
    url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={POLYGON_API_KEY}"
    resp = requests.get(url).json()

    try:
        return float(resp["results"]["share_class_shares_outstanding"])
    except (KeyError, TypeError):
        raise Exception(f"Could not fetch shares outstanding for {ticker}")
