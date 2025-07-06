import os
import io
import datetime as dt
import time
import xml.etree.ElementTree as ET
from typing import Tuple, List

import pandas as pd
import requests
from ibflex import parser

FLEX_BASE = "https://gdcdyn.interactivebrokers.com/Universal/servlet"

TOKEN = os.environ.get("IBKR_FLEX_TOKEN")
QUERY_ID = os.environ.get("IBKR_FLEX_QUERY_ID")
HEADERS = {"User-Agent": "Python/3"}


def fetch_flex_xml(from_date: dt.date, to_date: dt.date) -> str:
    """Download one Flex statement (<=365 days) and return the raw XML."""
    if not TOKEN or not QUERY_ID:
        raise EnvironmentError("IBKR_FLEX_TOKEN and IBKR_FLEX_QUERY_ID must be set")

    send_req = (
        f"{FLEX_BASE}/FlexStatementService.SendRequest"
        f"?v=3&t={TOKEN}&q={QUERY_ID}"
        f"&fromDate={from_date:%Y%m%d}&toDate={to_date:%Y%m%d}"
    )
    resp = requests.get(send_req, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    ref_code = ET.fromstring(resp.text).findtext(".//ReferenceCode")
    if ref_code is None:
        raise RuntimeError(f"SendRequest failed:\n{resp.text}")

    get_stmt = (
        f"{FLEX_BASE}/FlexStatementService.GetStatement"
        f"?v=3&t={TOKEN}&q={ref_code}"
    )
    for _ in range(30):
        stmt_resp = requests.get(get_stmt, headers=HEADERS, timeout=30)
        stmt_resp.raise_for_status()
        if "<ErrorCode>1019" not in stmt_resp.text:
            return stmt_resp.text
        time.sleep(10)
    raise TimeoutError("IBKR never finished generating the statement")


def fetch_statements(start_year: int, end_year: int | None = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Download Flex statements year by year and return trades and cash DataFrames."""
    if end_year is None:
        end_year = dt.date.today().year

    trade_rows: List[dict] = []
    cash_rows: List[dict] = []

    for yr in range(start_year, end_year + 1):
        xml_text = fetch_flex_xml(
            from_date=dt.date(yr, 1, 1),
            to_date=dt.date(yr, 12, 31),
        )
        stmt = parser.parse(io.StringIO(xml_text)).FlexStatements[0]
        trade_rows += [t.__dict__ for t in stmt.Trades]
        cash_rows += [c.__dict__ for c in stmt.CashTransactions]

    trades_df = pd.DataFrame(trade_rows)
    cash_df = pd.DataFrame(cash_rows)
    return trades_df, cash_df
