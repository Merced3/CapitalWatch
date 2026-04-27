from dataclasses import asdict, is_dataclass
import json
from pathlib import Path


def normalize_record(record):
    if isinstance(record, dict):
        return record

    if hasattr(record, "to_dict"):
        return record.to_dict()

    if is_dataclass(record):
        return asdict(record)

    if hasattr(record, "__dict__"):
        return dict(record.__dict__)

    raise TypeError(f"Unsupported record type: {type(record)!r}")


def project_record(record, fields=None):
    normalized = normalize_record(record)

    if fields is None:
        return normalized

    return {field: normalized.get(field) for field in fields}


class JsonlRecordWriter:
    """Generic JSONL writer for iterable record exports."""

    def __init__(self, path):
        self.path = Path(path)

    def write_records(self, records, fields=None):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        count = 0
        with self.path.open("w", encoding="utf-8") as handle:
            for record in records:
                json.dump(project_record(record, fields=fields), handle, ensure_ascii=False)
                handle.write("\n")
                count += 1

        return count
