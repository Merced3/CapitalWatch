from dataclasses import asdict, dataclass


@dataclass
class FinancialInputs:
    ticker: str
    ebit: float
    assets: float
    liabilities: float
    current_assets: float
    current_liabilities: float
    cash: float
    debt: float
    market_cap: float
    accuracies: dict
    start_date: str
    end_date: str

    def to_dict(self):
        return asdict(self)


@dataclass
class MagicFormulaResult:
    ticker: str
    earnings_yield: float
    roc: float
    accuracy: str

    def to_dict(self):
        return asdict(self)


@dataclass
class RawCompanyDataSnapshot:
    ticker: str
    shares_outstanding: float
    accuracies: dict
    raw_api_data: dict

    def to_dict(self):
        return asdict(self)
