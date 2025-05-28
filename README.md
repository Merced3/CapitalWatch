# 📊 Capital Compounder Strategy

An automated stock scanner and ranking engine built to identify the most capital-efficient public companies based on fundamental analysis. Inspired by Joel Greenblatt’s “The Little Book That Still Beats the Market,” this tool evaluates companies using two key metrics: **Earnings Yield (EY)** and **Return on Capital (ROC)**.

---

## 🧠 What It Does

This project fetches real-time financial statements from the Polygon.io API and:

- Calculates **Earnings Yield** = EBIT / Enterprise Value
- Calculates **Return on Capital** = EBIT / (Net Fixed Assets + Working Capital)
- Assigns **accuracy levels** to each data point (🟢 accurate, 🟠 estimated, 🔴 rough)
- Groups results by fiscal period
- Saves raw financials locally for transparency
- Ranks all companies from best to worst based on capital efficiency

---

## 🔎 Who It's For

- Long-term investors who want a disciplined, data-driven way to evaluate stocks
- Fans of Joel Greenblatt’s Magic Formula strategy
- Developers looking to automate equity screening and valuation
- Quant-minded individuals who prefer to **own shares of great businesses** with solid fundamentals

---

## 📁 Project Structure

```bash
.
├── company_data/                 # Saved JSONs of financial snapshots
│   ├── partial/                 # Companies missing key financials
├── tickers.txt                  # Tickers to evaluate (one per line)
├── scan.py                      # Main execution script
├── utils.py                     # Core logic (fetching, parsing, calculations)
├── config_example.py            # Template for your Polygon API key
├── requirements.txt             # Python packages required
├── .gitignore                   # Ignores API key and saved financials
└── README.md                    # This file
```

---

## 📈 Key Metrics

### Earnings Yield (EY)

How much a company earns (EBIT) relative to what it would cost to buy it (Enterprise Value).

### Return on Capital (ROC)

How efficiently a company generates profits relative to capital employed.

---

## ✅ Output Example

```bash
📊 Capital Efficiency Scan:

❌ GTLB: Missing 'income_statement'
❌ ITA: No data found

| Data Period: Jan 01 - Mar 31, 2025 |
🟢 HOOD: EY=1.73% | ROC=2.51% | Accurate Calculations
🟠 PLTR: EY=0.13% | ROC=3.09% | Estimated → cash, debt

🏆 All Stocks Ranked (Best to Worst):
🟢 NVDA: EY=2.51% | ROC=57.6%
🟠 PLTR: EY=0.13% | ROC=3.09%
🟢 HOOD: EY=1.73% | ROC=2.51%
```

---

## ⚙️ How to Use

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Add your Polygon API key**  
   Rename `config_example.py` to `config.py` and add your API key:

   ```python
   POLYGON_API_KEY = "your_api_key"
   BASE_URL = "https://api.polygon.io/vX/reference/financials"  # change `vX` to correct version
   ```

3. **Add tickers**  
   Populate `tickers.txt` with one stock ticker per line.

4. **Run the scanner**  

   ```bash
   python scan.py
   ```

---

## 🚀 Future Plans

This system is being expanded into a full **long-term investment bot** that will:

- Auto-discover and filter quality stocks weekly
- Deposit funds and allocate into top-ranked stocks
- Integrate with Interactive Brokers (IBKR) for automatic trades
- Send trade alerts and summaries to Discord via bot
- Track performance, risk, cash available, and portfolio value

---

## 🙏 Inspiration

This project is deeply inspired by:

- **Joel Greenblatt’s Magic Formula**
- Quantitative value investing practices
- The idea that consistent, rational investing beats prediction-based trading

---

## 🛡️ Disclaimer

This is a personal project for research and educational purposes. It is **not financial advice**. Use at your own risk.

---

## 🧠 Author

Built with discipline, automation, and a long-term mindset by [Merced Gonzales](https://github.com/yourgithubusername).

---

## ⭐️ Contributions Welcome

Have ideas, features, or bug fixes? Fork this repo, make your changes, and open a pull request!
