# ============================================================
# DATA FETCHING
# ============================================================

import yfinance as yf


# =========================
# FETCH STOCK DATA
# =========================
def fetch_data(stocks, period):
    tickers = [f"{s}.NS" for s in stocks]

    data = yf.download(
        tickers,
        period=period,
        interval="1d",
        auto_adjust=True
    )

    adj_close = data["Close"]

    if adj_close.empty:
        raise ValueError("No data fetched. Check stock symbol")

    return adj_close