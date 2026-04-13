from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_TICKER_FILE = PROJECT_ROOT / "data" / "universe" / "tickers.txt"
TEST_TICKER_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "tickers.txt"
RAW_COMPANY_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "company_data"

MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY", "YOUR_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")

if not MASSIVE_API_KEY:
    MASSIVE_API_KEY = POLYGON_API_KEY
if not POLYGON_API_KEY:
    POLYGON_API_KEY = MASSIVE_API_KEY

MASSIVE_FINANCIALS_URL = os.getenv("MASSIVE_FINANCIALS_URL", "")
BASE_URL = os.getenv("BASE_URL", "")

if not MASSIVE_FINANCIALS_URL and not BASE_URL:
    BASE_URL = "https://api.polygon.io/vX/reference/financials"

if not MASSIVE_FINANCIALS_URL:
    MASSIVE_FINANCIALS_URL = BASE_URL
if not BASE_URL:
    BASE_URL = MASSIVE_FINANCIALS_URL


def get_massive_api_key():
    return MASSIVE_API_KEY or POLYGON_API_KEY


def get_massive_financials_url():
    return MASSIVE_FINANCIALS_URL or BASE_URL


def ensure_runtime_directories():
    DEFAULT_TICKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    RAW_COMPANY_DATA_DIR.mkdir(parents=True, exist_ok=True)
