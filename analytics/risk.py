# ============================================================
# RISK
# ============================================================

import math


# =========================
# VOLATILITY
# =========================
def portfolio_volatility(portfolio_returns):
    return portfolio_returns.std() * math.sqrt(252)


# =========================
# RISK CLASSIFICATION
# =========================
def classify_risk(volatility):
    if volatility < 0.15:
        return "Low"
    elif volatility < 0.25:
        return "Moderate"
    else:
        return "High"


# =========================
# MAX DRAWDOWN
# =========================
def max_drawdown(portfolio_returns):
    cumulative = (1 + portfolio_returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return drawdown.min()