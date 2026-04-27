import sys

from capitalwatch.services.universe_service import MassiveActiveTickerSource


def main():
    source = MassiveActiveTickerSource()
    print(
        "Fetching active U.S. stock tickers from Massive...",
        file=sys.stderr,
        flush=True,
    )

    try:
        count = 0
        for ticker in source.iter_tickers():
            print(ticker, flush=True)
            count += 1

        print(f"Printed {count} tickers.", file=sys.stderr, flush=True)
    except Exception as exc:
        print(f"Universe fetch failed: {exc}", file=sys.stderr, flush=True)
        raise


if __name__ == "__main__":
    main()
