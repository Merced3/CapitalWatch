def rank_results(results):
    return sorted(results, key=_combined_score, reverse=True)


def _combined_score(result):
    if hasattr(result, "earnings_yield") and hasattr(result, "roc"):
        return result.earnings_yield + result.roc

    return result["earnings_yield"] + result["roc"]
