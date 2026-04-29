# ============================================================
# RETURNS
# ============================================================

import numpy as np


# =========================
# COMPUTE RETURNS
# =========================
def compute_returns(df):
    return df.pct_change().dropna()


# =========================
# PORTFOLIO RETURNS
# =========================
def portfolio_return(returns, weights=None):
    if weights is None:
        return returns.mean(axis=1)

    weights = np.array(weights)
    return (returns * weights).sum(axis=1)