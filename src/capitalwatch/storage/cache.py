import json
from pathlib import Path

from capitalwatch import config


class LocalRawCompanyDataCache:
    """Temporary file-backed adapter for raw company-data inspection."""

    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir is not None else config.RAW_COMPANY_DATA_DIR

    def save_snapshot(self, snapshot, partial=False):
        folder = self.base_dir / "partial" if partial else self.base_dir
        folder.mkdir(parents=True, exist_ok=True)

        filepath = folder / f"{snapshot.ticker}_financials.json"
        with filepath.open("w", encoding="utf-8") as handle:
            json.dump(snapshot.to_dict(), handle, indent=4)

        return filepath
