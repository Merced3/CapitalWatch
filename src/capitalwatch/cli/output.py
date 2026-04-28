from datetime import datetime
import sys


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


def print_scan_report(report):
    print(f"\n{DISPLAY_SYMBOLS['header']} Capital Efficiency Scan:\n")

    for error in report.errors:
        print(f"{DISPLAY_SYMBOLS['error']} {error.ticker}: {error.error}")

    for period, entries in report.entries_by_period.items():
        print(format_date_range(*period))
        for entry in entries:
            print(format_scan_entry(entry))

    print(f"\n{DISPLAY_SYMBOLS['ranking']} All Stocks Ranked (Best to Worst):\n")

    for result in report.ranked_results:
        emoji = DISPLAY_SYMBOLS[result.accuracy]
        print(f"{emoji} {result.ticker}: EY={result.earnings_yield}% | ROC={result.roc}%")


def format_scan_entry(entry):
    emoji = DISPLAY_SYMBOLS[entry.result.accuracy]
    explanation = describe_accuracy(entry.result.accuracy, entry.financials.accuracies)
    return (
        f"{emoji} {entry.result.ticker}: EY={entry.result.earnings_yield}% | "
        f"ROC={entry.result.roc}% | {explanation}"
    )


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
