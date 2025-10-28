
# ======= US sectors vs S&P 500 (relative, ba had aseline 2020-01-02) =======
# Usage:
#   pip install yfinance pandas numpy matplotlib
#   python us_vs_benchmark.py
#
# Output:
#   us_relative_vs_spy.csv  (relative-normalized index = 100 at baseline)
#   us_relative_vs_spy.png  (line chart with baseline marker)

import pandas as pd, numpy as np, yfinance as yf
import matplotlib.pyplot as plt
from datetime import date

# ---------- Sector universe (14) ----------
US_SECTORS = [
    "XLK","XLV","XLE","XRT","XLP","IGV","XLB","XLU",
    "ITA","XLI","XLY","ITB","IYT","CARZ"
]

BENCH = "SPY"                 # S&P 500 ETF (total-return proxy via Adj Close)
START, END = "2019-01-01", str(date.today())
BASELINE = "2020-01-02"       # COVID shock baseline

def download_prices(tickers, start=START, end=END):
    df = yf.download(tickers, start=start, end=end, auto_adjust=False)["Adj Close"]
    return df.dropna(how="all", axis=1)

def relative_normalized(sector_df: pd.DataFrame, bench: pd.Series, baseline_date: str) -> tuple[pd.DataFrame, pd.Timestamp]:
    # Find nearest actual trading day to the requested baseline
    bidx = sector_df.index.get_indexer([pd.to_datetime(baseline_date)], method="nearest")[0]
    bdate_used = sector_df.index[bidx]
    # Relative to benchmark
    rel = sector_df.divide(bench, axis=0)
    # Normalize to 100 at baseline
    rel_norm = rel / rel.iloc[bidx] * 100.0
    return rel_norm, bdate_used

def main():
    tickers = [BENCH] + US_SECTORS
    data = download_prices(tickers)
    if data.empty or BENCH not in data.columns:
        raise SystemExit("No data downloaded or benchmark missing; check internet or tickers.")
    bench = data[BENCH]
    sectors = data[US_SECTORS].dropna(axis=1, how="all")

    rel_norm, bdate_used = relative_normalized(sectors, bench, BASELINE)

    # Save CSV
    rel_norm.to_csv("us_relative_vs_spy.csv")
    print("Saved: us_relative_vs_spy.csv")

    # Plot
    ax = rel_norm.plot(figsize=(12,6), linewidth=1)
    ax.set_title(f"US Sectors vs S&P 500 (SPY) — Relative, normalized to 100 at {bdate_used.date()}")
    ax.set_ylabel("Relative Index (Sector / SPY, baseline = 100)")
    ax.grid(True, alpha=0.3)
    ax.axvline(bdate_used, linestyle="--")
    ax.annotate("COVID baseline", xy=(bdate_used, ax.get_ylim()[1]), xytext=(5, -20),
                textcoords="offset points", ha="left", va="top")
    plt.tight_layout()
    plt.savefig("us_relative_vs_spy.png", dpi=150)
    plt.show()
    print("Saved: us_relative_vs_spy.png")

if __name__ == "__main__":
    main()
