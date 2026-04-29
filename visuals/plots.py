# ============================================================
# VISUALS
# ============================================================

import plotly.graph_objects as go
import numpy as np
from analytics.sector import get_sector


# =========================
# STYLE
# =========================
BASE_FONT = dict(family="Inter, Roboto, Arial", size=13, color="white")
TITLE_STYLE = dict(family="Montserrat, Inter", size=22, color="white")

BG_COLOR = "#111111"
GRID_COLOR = "#333333"


# =========================
# PORTFOLIO GROWTH
# =========================
def portfolio_growth(portfolio_returns):
    port_cum = (1 + portfolio_returns).cumprod()

    port_return = (port_cum.iloc[-1].item() - 1) * 100
    sign = "+" if port_return > 0 else ""

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=port_cum.index,
        y=port_cum,
        mode='lines',
        name='Portfolio',
        line=dict(color="#00FFAA", width=2)
    ))

    fig.update_layout(
        title=dict(text="Portfolio Performance", x=0.5),
        xaxis_title="Date",
        yaxis_title="Growth (₹1 invested)",

        template="plotly_dark",
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,

        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR),

        font=BASE_FONT,
        title_font=TITLE_STYLE,

        annotations=[
            dict(
                text=f"<b>Total Return: {sign}{port_return:.2f}%</b>",
                x=0.5,
                y=1.05,
                xref='paper',
                yref='paper',
                showarrow=False
            )
        ],

        margin=dict(t=90, b=60)
    )

    return fig


# =========================
# CORRELATION HEATMAP
# =========================
def correlation_heatmap(returns):
    corr = returns.corr()
    labels = [col.replace(".NS", "") for col in corr.columns]

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=labels,
        y=labels,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        text=corr.values.round(2),
        texttemplate="%{text}"
    ))

    fig.update_layout(
        title=dict(text="Correlation Matrix", x=0.5),
        template="plotly_dark",
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        font=BASE_FONT,
        title_font=TITLE_STYLE,
        margin=dict(t=80, b=60)
    )

    return fig


# =========================
# STOCK ALLOCATION
# =========================
def allocation_pie_chart(weights, stocks):

    if isinstance(weights, np.ndarray):
        values = weights
        labels = [s.replace(".NS", "") for s in stocks]
    else:
        labels = [k.replace(".NS", "") for k in weights.keys()]
        values = list(weights.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        textinfo='percent+label'
    )])

    fig.update_layout(
        title=dict(text="Stock Allocation", x=0.5),
        template="plotly_dark",
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        font=BASE_FONT,
        title_font=TITLE_STYLE,
        margin=dict(t=80, b=60)
    )

    return fig


# =========================
# SECTOR ALLOCATION
# =========================
def sector_allocation_pie(stocks, weights):

    if isinstance(weights, np.ndarray):
        weights_dict = dict(zip(stocks, weights))
    else:
        weights_dict = weights

    sector_weights = {}

    for stock, w in weights_dict.items():
        sector = get_sector(stock) or "Unknown"
        sector_weights[sector] = sector_weights.get(sector, 0) + w

    labels = list(sector_weights.keys())
    values = list(sector_weights.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        textinfo='percent+label'
    )])

    fig.update_layout(
        title=dict(text="Sector Allocation", x=0.5),
        template="plotly_dark",
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        font=BASE_FONT,
        title_font=TITLE_STYLE,
        margin=dict(t=80, b=60)
    )

    return fig


# =========================
# CONTRIBUTION CHART
# =========================
def contribution_chart(stocks, contributions):

    labels = [s.replace(".NS", "") for s in stocks]

    colors = ["#00FFAA" if v >= 0 else "#FF4D4D" for v in contributions]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels,
        y=contributions,
        marker=dict(color=colors),
        text=[f"{v:.2%}" for v in contributions],
        textposition='outside'
    ))

    fig.update_layout(
        title=dict(text="Contribution to Portfolio Return", x=0.5),
        xaxis_title="Stocks",
        yaxis_title="Contribution",

        template="plotly_dark",
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,

        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR),

        font=BASE_FONT,
        title_font=TITLE_STYLE,

        margin=dict(t=80, b=80)
    )

    return fig


# =========================
# RISK vs RETURN
# =========================
def risk_return_scatter(returns):

    mean_returns = returns.mean() * 252
    volatility = returns.std() * np.sqrt(252)

    labels = [col.replace(".NS", "") for col in returns.columns]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=volatility,
        y=mean_returns,
        mode='markers+text',
        text=labels,
        textposition="top center",
        marker=dict(size=12, color="#4CC9F0")
    ))

    fig.update_layout(
        title=dict(text="Risk vs Return", x=0.5),
        xaxis_title="Risk (Volatility)",
        yaxis_title="Return",

        template="plotly_dark",
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,

        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR),

        font=BASE_FONT,
        title_font=TITLE_STYLE,

        margin=dict(t=80, b=60)
    )

    return fig