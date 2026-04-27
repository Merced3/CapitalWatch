# CapitalWatch

CapitalWatch scans a list of ticker symbols, fetches financial data through the current Massive-compatible API flow, calculates Joel Greenblatt-style Magic Formula metrics, and ranks the results.

## Current Layout

```text
.
|-- data/
|   |-- raw/company_data/         # Saved raw company snapshots
|   |   `-- partial/              # Snapshots for incomplete financials
|   `-- universe/tickers.txt      # Runtime ticker source
|-- src/capitalwatch/
|   |-- cli.py                    # Main scan pipeline
|   |-- config.py                 # Local runtime config
|   |-- clients/
|   |-- services/
|   |-- storage/
|   `-- domain/
|-- tests/
|   |-- fixtures/tickers.txt      # Small manual ticker fixture
|   `-- old_code/                 # Reference-only legacy code
|-- setup.py
`-- requirements.txt
```

## Setup

1. Install dependencies.

```bash
pip install -r requirements.txt
pip install -e .
```

2. Add your API key.

Preferred option in PowerShell:

```powershell
$env:MASSIVE_API_KEY = "your_api_key"
```

Compatibility variables still supported:

```powershell
$env:POLYGON_API_KEY = "your_api_key"
$env:BASE_URL = "https://api.polygon.io/vX/reference/financials"
```

If you prefer file-based local config, edit `src/capitalwatch/config.py` and replace the placeholder fallback string.

3. Put ticker symbols in `data/universe/tickers.txt`.

## Run

```bash
capitalwatch
```

After editable install, this also works:

```bash
python -m capitalwatch
```

## Print The Active Stock Universe

This is a separate process from the scan/rank pipeline and only prints the current active stock tickers from the Massive-backed reference endpoint.

```bash
capitalwatch-universe
```

After editable install, this also works:

```bash
python -m capitalwatch.universe_cli
```

## Save The Active Stock Universe

This is a separate export process. It saves ticker records from the same Massive universe endpoint to JSONL so the data can be reused later without coupling storage to the fetch logic.

Save full records:

```bash
capitalwatch-universe-export
```

Save only selected fields:

```bash
capitalwatch-universe-export --fields ticker name market locale type active primary_exchange
```

Default output path:

```text
data/output/universe/active_us_stocks.jsonl
```

## Notes

- Raw saved company data is temporary and currently goes to `data/raw/company_data/`.
- The ticker source is temporary and currently comes from `data/universe/tickers.txt`.
- The current universe fetcher is broad by design: active U.S. stock-market tickers. It is not yet a final curated "investable company" universe and may include multiple stock-market instrument types.
- `tests/fixtures/tickers.txt` is available for small manual test runs.
- The legacy code under `tests/old_code/` is retained as reference only.
