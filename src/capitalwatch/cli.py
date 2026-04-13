from collections import defaultdict
from datetime import datetime
import sys

from capitalwatch import config
from capitalwatch.clients.massive_client import MassiveClient
from capitalwatch.services.financials_service import FinancialsService
from capitalwatch.services.ranking_service import rank_results
from capitalwatch.services.universe_service import load_tickers
from capitalwatch.storage.cache import LocalRawCompanyDataCache

def _build_display_symbols():
    unicode_symbols = {
        "header": "\U0001F4CA",
        "ranking": "\U0001F3C6",
        "error": "\u274C",
        "accurate": "\U0001F7E2",
        "estimated": "\U0001F7E1",
        "estimated_strong": "\U0001F7E1",
        "estimated_weak": "\U0001F7E0",
        "rough": "\U0001F534",
    }

    encoding = sys.stdout.encoding or "utf-8"
    try:
        "".join(unicode_symbols.values()).encode(encoding)
        return unicode_symbols
    except UnicodeEncodeError:
        return {
            "header": "[Scan]",
            "ranking": "[Rank]",
            "error": "[Error]",
            "accurate": "[A]",
            "estimated": "[E]",
            "estimated_strong": "[E+]",
            "estimated_weak": "[E]",
            "rough": "[R]",
        }


DISPLAY_SYMBOLS = _build_display_symbols()


def main():
    run_scan()


def run_scan(tickers=None, ticker_source=None, financials_service=None):
    config.ensure_runtime_directories()

    if financials_service is None:
        financials_service = FinancialsService(
            client=MassiveClient(),
            cache=LocalRawCompanyDataCache(),
        )

    if tickers is None:
        tickers = load_tickers(ticker_source)
    else:
        tickers = load_tickers(tickers)

    print(f"\n{DISPLAY_SYMBOLS['header']} Capital Efficiency Scan:\n")

    grouped = defaultdict(list)
    all_results = []

    for ticker in tickers:
        try:
            financials = financials_service.fetch_financials(ticker)
            result = financials_service.calculate_magic_formula(financials)
            emoji = DISPLAY_SYMBOLS[result.accuracy]
            label = format_date_range(financials.start_date, financials.end_date)
            explanation = describe_accuracy(result.accuracy, financials.accuracies)
            line = (
                f"{emoji} {result.ticker}: EY={result.earnings_yield}% | "
                f"ROC={result.roc}% | {explanation}"
            )

            grouped[label].append(line)
            all_results.append(result)
        except Exception as exc:
            print(f"{DISPLAY_SYMBOLS['error']} {ticker}: {exc}")

    for period, lines in grouped.items():
        print(period)
        for line in lines:
            print(line)

    print(f"\n{DISPLAY_SYMBOLS['ranking']} All Stocks Ranked (Best to Worst):\n")

    ranked = rank_results(all_results)
    for result in ranked:
        emoji = DISPLAY_SYMBOLS[result.accuracy]
        print(f"{emoji} {result.ticker}: EY={result.earnings_yield}% | ROC={result.roc}%")

    return ranked


def describe_accuracy(accuracy, accuracies):
    if accuracy == "accurate":
        return "Accurate Calculations"

    if accuracy.startswith("estimated"):
        confidence = "Strong" if "strong" in accuracy else "Weak"
        missing = [key for key, value in accuracies.items() if "estimated" in value or value == "rough"]
        return f"{confidence} Estimate -> " + ", ".join(missing)

    missing = [key for key, value in accuracies.items() if value == "rough"]
    return "Rough Estimate -> " + ", ".join(missing)


def format_date_range(start_str, end_str):
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")

    if start.year == end.year:
        return f"\n| Data Period: {start.strftime('%b %d')} - {end.strftime('%b %d')}, {start.year} |"

    return f"\n| Data Period: {start.strftime('%b %d, %Y')} - {end.strftime('%b %d, %Y')} |"


if __name__ == "__main__":
    main()
