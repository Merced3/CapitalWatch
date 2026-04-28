from collections import defaultdict
from dataclasses import dataclass, field

from capitalwatch.clients.massive_client import MassiveClient
from capitalwatch.services.financials_service import FinancialsService
from capitalwatch.services.ranking_service import rank_results
from capitalwatch.services.universe_service import load_tickers
from capitalwatch.storage.cache import LocalRawCompanyDataCache


@dataclass
class ScanEntry:
    financials: object
    result: object


@dataclass
class ScanError:
    ticker: str
    error: Exception


@dataclass
class ScanReport:
    entries_by_period: dict = field(default_factory=dict)
    ranked_results: list = field(default_factory=list)
    errors: list = field(default_factory=list)


class ScanService:
    def __init__(self, financials_service=None):
        self.financials_service = financials_service or FinancialsService(
            client=MassiveClient(),
            cache=LocalRawCompanyDataCache(),
        )

    def run(self, tickers=None, ticker_source=None):
        if tickers is None:
            tickers = load_tickers(ticker_source)
        else:
            tickers = load_tickers(tickers)

        entries_by_period = defaultdict(list)
        all_results = []
        errors = []

        for ticker in tickers:
            try:
                financials = self.financials_service.fetch_financials(ticker)
                result = self.financials_service.calculate_magic_formula(financials)
                period_key = (financials.start_date, financials.end_date)

                entries_by_period[period_key].append(
                    ScanEntry(financials=financials, result=result)
                )
                all_results.append(result)
            except Exception as exc:
                errors.append(ScanError(ticker=ticker, error=exc))

        return ScanReport(
            entries_by_period=dict(entries_by_period),
            ranked_results=rank_results(all_results),
            errors=errors,
        )
