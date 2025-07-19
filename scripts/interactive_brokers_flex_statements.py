from pathlib import Path
import pandas as pd

from financial_investing_platform.ibkr_flex import fetch_statements

if __name__ == "__main__":
    trades_df, cash_df = fetch_statements(start_year=2017)

    trades_file = Path("ibkr_trades.parquet")
    cash_file = Path("ibkr_cash.parquet")

    trades_df.to_parquet(trades_file)
    cash_df.to_parquet(cash_file)

    print(f"Saved {len(trades_df):,} trades and {len(cash_df):,} cash rows.")
    print(f"Trade data -> {trades_file.resolve()}")
    print(f"Cash data  -> {cash_file.resolve()}")
