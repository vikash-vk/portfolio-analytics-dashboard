# ============================================================
# PORTFOLIO METRICS
# ============================================================

import numpy as np
import math


# =========================
# DIVERSIFICATION
# =========================
def diversification_score(returns):
    corr = returns.corr()
    avg_corr = corr.where(~np.eye(corr.shape[0], dtype=bool)).mean().mean()
    return avg_corr


def classify_diversification(avg_corr):
    if avg_corr > 0.7:
        return "Poor"
    elif avg_corr > 0.4:
        return "Moderate"
    else:
        return "Good"


# =========================
# SHARPE RATIO
# =========================
def sharpe_ratio(portfolio_returns):
    mean_return = portfolio_returns.mean()
    std_dev = portfolio_returns.std()

    if std_dev == 0:
        return 0

    return (mean_return / std_dev) * math.sqrt(252)


# =========================
# CONTRIBUTION ANALYSIS
# =========================
def contribution_analysis(returns, weights=None):

    if weights is None:
        cumulative_returns = (1 + returns).prod() - 1
        best = cumulative_returns.idxmax()
        worst = cumulative_returns.idxmin()
        return best, worst, cumulative_returns

    weights = np.array(weights)

    contributions = []

    for i, col in enumerate(returns.columns):
        stock_contribution = returns[col] * weights[i]
        stock_cum = (1 + stock_contribution).cumprod()
        contrib_value = stock_cum.iloc[-1] - 1
        contributions.append(contrib_value)

    contributions = np.array(contributions)

    best = returns.columns[np.argmax(contributions)]
    worst = returns.columns[np.argmin(contributions)]

    return best, worst, contributions