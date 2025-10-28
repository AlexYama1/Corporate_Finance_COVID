
# ======= Japan sectors vs Nikkei 225 (relative, baseline 2020-01-02) =======
# Usage:
#   pip install yfinance pandas numpy matplotlib
#   python jp_vs_benchmark.py
#
# Output:
#   jp_relative_vs_n225.csv  (relative-normalized index = 100 at baseline)
#   jp_relative_vs_n225.png  (line chart with baseline marker)

import pandas as pd, numpy as np, yfinance as yf
import matplotlib.pyplot as plt
from datetime import date

# ---------- Sector universe (14, TOPIX-17 mapped) ----------
JAPAN_SECTORS = [
    "1625.T","1621.T","1618.T","1629.T","1617.T","1626.T","1620.T","1627.T",
    "1624.T","1623.T","1630.T","1619.T","1628.T","1622.T"
]

BENCH = "1321.T"              # Nikkei 225 ETF (Nomura); ETFs give dividend-adjusted series via Adj Close
START, END = "2019-01-01", str(date.today())
BASELINE = "2020-01-02"       # COVID shock baseline

def download_prices(tickers, start=START, end=END):
    df = yf.download(tickers, start=start, end=end, auto_adjust=False)["Adj Close"]
    return df.dropna(how="all", axis=1)

def relative_normalized(sector_df: pd.DataFrame, bench: pd.Series, baseline_date: str) -> tuple[pd.DataFrame, pd.Timestamp]:
    bidx = sector_df.index.get_indexer([pd.to_datetime(baseline_date)], method="nearest")[0]
    bdate_used = sector_df.index[bidx]
    rel = sector_df.divide(bench, axis=0)
    rel_norm = rel / rel.iloc[bidx] * 100.0
    return rel_norm, bdate_used

def main():
    tickers = [BENCH] + JAPAN_SECTORS
    data = download_prices(tickers)
    if data.empty or BENCH not in data.columns:
        raise SystemExit("No data downloaded or benchmark missing; check internet or tickers.")
    bench = data[BENCH]
    sectors = data[JAPAN_SECTORS].dropna(axis=1, how="all")

    rel_norm, bdate_used = relative_normalized(sectors, bench, BASELINE)

    # Save CSV
    rel_norm.to_csv("jp_relative_vs_n225.csv")
    print("Saved: jp_relative_vs_n225.csv")

    # Plot
    ax = rel_norm.plot(figsize=(12,6), linewidth=1)
    ax.set_title(f"Japan Sectors vs Nikkei 225 (1321.T) — Relative, normalized to 100 at {bdate_used.date()}")
    ax.set_ylabel("Relative Index (Sector / Nikkei225 ETF, baseline = 100)")
    ax.grid(True, alpha=0.3)
    ax.axvline(bdate_used, linestyle="--")
    ax.annotate("COVID baseline", xy=(bdate_used, ax.get_ylim()[1]), xytext=(5, -20),
                textcoords="offset points", ha="left", va="top")
    plt.tight_layout()
    plt.savefig("jp_relative_vs_n225.png", dpi=150)
    plt.show()
    print("Saved: jp_relative_vs_n225.png")

if __name__ == "__main__":
    main()
