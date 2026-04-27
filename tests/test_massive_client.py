import unittest

from capitalwatch.clients.massive_client import MassiveClient


class StubResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"status": "OK", "results": []}


class StubSession:
    def __init__(self):
        self.calls = []

    def get(self, url, params=None):
        self.calls.append({"url": url, "params": params})
        return StubResponse()


class MassiveClientTests(unittest.TestCase):
    def test_fetch_reference_tickers_includes_api_key_on_first_page(self):
        session = StubSession()
        client = MassiveClient(api_key="test-key", session=session)

        client.fetch_reference_tickers(params={"locale": "us", "market": "stocks"})

        self.assertEqual(
            session.calls[0]["params"],
            {"locale": "us", "market": "stocks", "apiKey": "test-key"},
        )


if __name__ == "__main__":
    unittest.main()
