# ============================================================
# SECTOR
# ============================================================

import yfinance as yf
import numpy as np


# =========================
# GET SECTOR
# =========================
def get_sector(stock):
    try:
        ticker = yf.Ticker(f"{stock}.NS")
        return ticker.info.get("sector")
    except Exception:
        return None


# =========================
# SECTOR BREAKDOWN
# =========================
def sector_breakdown(stocks, weights=None):
    if weights is None:
        weights = np.ones(len(stocks)) / len(stocks)

    sector_map = {}
    sector_weight = {}
    missing = []

    for stock, weight in zip(stocks, weights):
        sector = get_sector(stock)

        if sector:
            if sector not in sector_map:
                sector_map[sector] = []
                sector_weight[sector] = 0

            sector_map[sector].append(stock)
            sector_weight[sector] += weight
        else:
            missing.append(stock)

    return sector_map, sector_weight, missing