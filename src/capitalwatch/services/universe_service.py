from pathlib import Path

from capitalwatch import config


class FileTickerSource:
    """Temporary text-file ticker source until universe acquisition is replaced."""

    def __init__(self, path=None):
        self.path = Path(path) if path is not None else config.DEFAULT_TICKER_FILE

    def load_tickers(self):
        with self.path.open("r", encoding="utf-8") as handle:
            return normalize_tickers(handle)


def normalize_tickers(tickers):
    return [ticker.strip().upper() for ticker in tickers if ticker.strip()]


def load_tickers(source=None):
    if source is None:
        return FileTickerSource().load_tickers()

    if isinstance(source, (str, Path)):
        return FileTickerSource(source).load_tickers()

    if hasattr(source, "load_tickers"):
        return normalize_tickers(source.load_tickers())

    return normalize_tickers(source)
