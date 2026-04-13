# scan.py

from datetime import datetime
from collections import defaultdict
from utils import fetch_financials, calculate_magic_formula, load_tickers

ACCURACY_EMOJIS = {
    "accurate": "🟢",
    "estimated_strong": "🟡",
    "estimated_weak": "🟠",
    "rough": "🔴"
}

def main():
    print("\n📊 Capital Efficiency Scan:\n")
    tickers = load_tickers()
    grouped = defaultdict(list)
    all_results = []

    for ticker in tickers:
        try:
            fin_data = fetch_financials(ticker)
            result = calculate_magic_formula(fin_data)
            emoji = ACCURACY_EMOJIS[result["accuracy"]]
            start = fin_data["start_date"]
            end = fin_data["end_date"]
            label = format_date_range(start, end)

            acc = result["accuracy"]
            
            if acc == "accurate":
                explanation = "Accurate Calculations"
            elif acc.startswith("estimated"):
                confidence = "Strong" if "strong" in acc else "Weak"
                missing = [k for k, v in fin_data["accuracies"].items() if "estimated" in v or v == "rough"]
                explanation = f"{confidence} Estimate → " + ", ".join(missing)
            else:
                missing = [k for k, v in fin_data["accuracies"].items() if v == "rough"]
                explanation = "Rough Estimate → " + ", ".join(missing)

            line = f"{emoji} {result['ticker']}: EY={result['earnings_yield']}% | ROC={result['roc']}% | {explanation}"
            grouped[label].append(line)
            result.update({
                "emoji": emoji,
                "line": line
            })
            all_results.append(result)

        except Exception as e:
            print(f"❌ {ticker}: {e}")

    # Print grouped output
    for period, lines in grouped.items():
        print(period)
        for line in lines:
            print(line)

    print("\n🏆 All Stocks Ranked (Best to Worst):\n")
    
    # Sort by combined metric — You can tweak this formula
    ranked = sorted(all_results, key=lambda x: (x['earnings_yield'] + x['roc']), reverse=True)

    for res in ranked:
        print(f"{res['emoji']} {res['ticker']}: EY={res['earnings_yield']}% | ROC={res['roc']}%")

def format_date_range(start_str, end_str):
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")
    same_year = start.year == end.year

    if same_year:
        return f"\n| Data Period: {start.strftime('%b %d')} - {end.strftime('%b %d')}, {start.year} |"
    else:
        return f"\n| Data Period: {start.strftime('%b %d, %Y')} - {end.strftime('%b %d, %Y')} |"

if __name__ == "__main__":
    main()
