import tempfile
import unittest
from pathlib import Path

from capitalwatch.storage.records import JsonlRecordWriter, project_record


class DictBackedObject:
    def to_dict(self):
        return {"ticker": "ANF", "score": 42}


class RecordWriterTests(unittest.TestCase):
    def test_project_record_keeps_selected_fields(self):
        record = {"ticker": "ANF", "name": "Abercrombie & Fitch", "market": "stocks"}

        self.assertEqual(
            project_record(record, fields=["ticker", "name"]),
            {"ticker": "ANF", "name": "Abercrombie & Fitch"},
        )

    def test_jsonl_writer_supports_to_dict_objects(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "records.jsonl"
            writer = JsonlRecordWriter(output_path)

            count = writer.write_records([DictBackedObject()], fields=["ticker"])

            self.assertEqual(count, 1)
            self.assertEqual(output_path.read_text(encoding="utf-8"), '{"ticker": "ANF"}\n')


if __name__ == "__main__":
    unittest.main()
