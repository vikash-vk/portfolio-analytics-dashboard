# ============================================================
# DIVIDENDS
# ============================================================

import yfinance as yf
import numpy as np
from datetime import datetime, timedelta


# =========================
# PERIOD TO DAYS
# =========================
PERIOD_TO_DAYS = {
    "1mo": 30,
    "3mo": 90,
    "6mo": 180,
    "1y": 365,
    "3y": 1095,
    "5y": 1825
}


# =========================
# SINGLE STOCK YIELD
# =========================
def get_dividend_yield(stock, period, start_date=None, price=None):
    try:
        ticker = yf.Ticker(f"{stock}.NS")
        dividends = ticker.dividends

        if dividends.empty:
            return 0

        days = PERIOD_TO_DAYS.get(period, 365)

        cutoff_date = (
            start_date
            if start_date is not None
            else datetime.today() - timedelta(days=days)
        )

        dividends.index = dividends.index.tz_localize(None)

        filtered_div = dividends[dividends.index >= cutoff_date]
        total_div = filtered_div.sum()

        if price is None or price == 0:
            return None

        return (total_div / price) * (365 / days)

    except Exception as e:
        print(f"Dividend fetch error for {stock}: {e}")
        return 0


# =========================
# PORTFOLIO YIELD
# =========================
def portfolio_dividend_yield(stocks, period, weights=None, start_date=None, prices=None):
    yields = {
        stock: get_dividend_yield(
            stock,
            period,
            start_date=start_date,
            price=prices.get(f"{stock}.NS") if prices is not None else None
        )
        for stock in stocks
    }

    if weights is None:
        return yields, sum(yields.values()) / len(stocks)

    weights = np.array(weights)
    yield_array = np.array([
    yields[s] if yields[s] is not None else 0
    for s in stocks
    ])

    return yields, np.dot(yield_array, weights)