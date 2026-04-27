import unittest

from capitalwatch.services.universe_service import MassiveActiveTickerSource


class StubMassiveClient:
    def __init__(self):
        self.calls = []

    def fetch_reference_tickers(self, params=None, next_url=None):
        self.calls.append({"params": params, "next_url": next_url})

        if next_url is None:
            return {
                "results": [
                    {"ticker": "anf"},
                    {"ticker": "hood"},
                ],
                "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=abc",
            }

        return {
            "results": [
                {"ticker": "pltr"},
            ]
        }


class MassiveActiveTickerSourceTests(unittest.TestCase):
    def test_load_tickers_paginates_and_normalizes(self):
        client = StubMassiveClient()
        source = MassiveActiveTickerSource(client=client)

        self.assertEqual(source.load_tickers(), ["ANF", "HOOD", "PLTR"])
        self.assertEqual(client.calls[0]["params"]["locale"], "us")
        self.assertEqual(client.calls[0]["params"]["market"], "stocks")
        self.assertEqual(client.calls[0]["params"]["active"], "true")
        self.assertEqual(client.calls[0]["params"]["limit"], 1000)
        self.assertEqual(client.calls[1]["next_url"], "https://api.polygon.io/v3/reference/tickers?cursor=abc")

    def test_iter_tickers_streams_normalized_values(self):
        client = StubMassiveClient()
        source = MassiveActiveTickerSource(client=client)

        self.assertEqual(list(source.iter_tickers()), ["ANF", "HOOD", "PLTR"])

    def test_missing_results_field_raises_clear_error(self):
        class BrokenClient:
            def fetch_reference_tickers(self, params=None, next_url=None):
                return {"status": "OK", "request_id": "abc"}

        source = MassiveActiveTickerSource(client=BrokenClient())

        with self.assertRaises(RuntimeError) as error:
            list(source.iter_ticker_records())

        self.assertIn("no results field", str(error.exception))


if __name__ == "__main__":
    unittest.main()
