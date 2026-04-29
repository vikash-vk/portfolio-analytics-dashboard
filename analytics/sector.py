# ============================================================
# SECTOR
# ============================================================

import pandas as pd
import numpy as np
from functools import lru_cache


# ============================================================
# LOAD SECTOR MAP
# ============================================================

@lru_cache(maxsize=1)
def load_sector_map():
    try:
        df = pd.read_csv("data/sector_map.csv")
        df["SYMBOL"] = df["SYMBOL"].astype(str).str.strip().str.upper()
        df["SECTOR"] = df["SECTOR"].astype(str).str.strip()
        return dict(zip(df["SYMBOL"], df["SECTOR"]))
    except Exception:
        return {}


# ============================================================
# GET SECTOR
# ============================================================

def get_sector(stock):
    symbol = str(stock).replace(".NS", "").strip().upper()
    sector_map = load_sector_map()
    return sector_map.get(symbol, None)


# ============================================================
# SECTOR BREAKDOWN
# ============================================================

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