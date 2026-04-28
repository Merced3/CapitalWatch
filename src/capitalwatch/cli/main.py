import argparse
import sys

from capitalwatch import config
from capitalwatch.cli.output import print_scan_report
from capitalwatch.services.scan_service import ScanService
from capitalwatch.services.universe_service import MassiveActiveTickerSource
from capitalwatch.storage.records import JsonlRecordWriter

DEFAULT_UNIVERSE_OUTPUT_PATH = config.OUTPUT_DATA_DIR / "universe" / "active_us_stocks.jsonl"


def build_parser():
    parser = argparse.ArgumentParser(description="CapitalWatch command line tools.")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Run the capital efficiency scan.")
    scan_parser.set_defaults(handler=run_scan_command)

    universe_parser = subparsers.add_parser("universe", help="Work with the active stock universe.")
    universe_subparsers = universe_parser.add_subparsers(dest="universe_command")

    universe_print_parser = universe_subparsers.add_parser(
        "print",
        help="Print active U.S. stock tickers.",
    )
    universe_print_parser.set_defaults(handler=run_universe_print_command)

    universe_export_parser = universe_subparsers.add_parser(
        "export",
        help="Save active U.S. stock ticker records as JSONL.",
    )
    universe_export_parser.add_argument(
        "--output",
        default=str(DEFAULT_UNIVERSE_OUTPUT_PATH),
        help="Output JSONL path.",
    )
    universe_export_parser.add_argument(
        "--fields",
        nargs="*",
        default=None,
        help="Optional list of fields to keep from each record. Default saves full records.",
    )
    universe_export_parser.set_defaults(handler=run_universe_export_command)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "handler") and args.command is None:
        return run_scan_command(args)
    if not hasattr(args, "handler"):
        parser.error("a subcommand is required")

    return args.handler(args)


def run_scan(tickers=None, ticker_source=None, financials_service=None):
    config.ensure_runtime_directories()
    report = ScanService(financials_service=financials_service).run(
        tickers=tickers,
        ticker_source=ticker_source,
    )
    print_scan_report(report)
    return report.ranked_results


def run_scan_command(args):
    run_scan()
    return 0


def run_universe_print_command(args):
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
        return 0
    except Exception as exc:
        print(f"Universe fetch failed: {exc}", file=sys.stderr, flush=True)
        raise


def run_universe_export_command(args):
    source = MassiveActiveTickerSource()
    writer = JsonlRecordWriter(args.output)

    print(
        f"Fetching active U.S. stock ticker records from Massive and saving to {args.output}...",
        file=sys.stderr,
        flush=True,
    )

    count = writer.write_records(source.iter_ticker_records(), fields=args.fields)
    print(f"Saved {count} records to {args.output}.", file=sys.stderr, flush=True)
    return 0
