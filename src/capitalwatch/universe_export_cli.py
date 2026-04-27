import argparse
import sys

from capitalwatch import config
from capitalwatch.services.universe_service import MassiveActiveTickerSource
from capitalwatch.storage.records import JsonlRecordWriter

DEFAULT_OUTPUT_PATH = config.OUTPUT_DATA_DIR / "universe" / "active_us_stocks.jsonl"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Fetch the active U.S. stock universe from Massive and save it as JSONL."
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Output JSONL path.",
    )
    parser.add_argument(
        "--fields",
        nargs="*",
        default=None,
        help="Optional list of fields to keep from each record. Default saves full records.",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    source = MassiveActiveTickerSource()
    writer = JsonlRecordWriter(args.output)

    print(
        f"Fetching active U.S. stock ticker records from Massive and saving to {args.output}...",
        file=sys.stderr,
        flush=True,
    )

    count = writer.write_records(source.iter_ticker_records(), fields=args.fields)
    print(f"Saved {count} records to {args.output}.", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
