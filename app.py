# ============================================================
# APP
# ============================================================

import html as html_lib

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

from analytics.dividends import portfolio_dividend_yield
from analytics.portfolio_metrics import (
    contribution_analysis,
    diversification_score,
    classify_diversification,
    sharpe_ratio,
)
from analytics.risk import classify_risk, max_drawdown, portfolio_volatility
from analytics.returns import compute_returns, portfolio_return
from analytics.sector import sector_breakdown
from signals.technical import technical_signal
from visuals.plots import (
    allocation_pie_chart,
    contribution_chart,
    correlation_heatmap,
    portfolio_growth,
    risk_return_scatter,
    sector_allocation_pie,
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Portfolio Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>

    html, body {
        font-size: 16px;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(55, 77, 120, 0.25) 0%, rgba(10, 14, 24, 1) 35%, rgba(7, 10, 18, 1) 100%),
            linear-gradient(180deg, #0B1020 0%, #080B12 100%);
        color: #F4F7FB;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    header [data-testid="stHeader"] {
        display: none;
    }

    .block-container {
        padding-top: 5rem;
        padding-bottom: 5rem;
        max-width: 1900px;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(15, 21, 38, 0.96) 0%, rgba(9, 13, 22, 0.94) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 30px;
        padding: 45px 50px;
        margin-bottom: 30px;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4);
    }

    .hero-title {
        font-size: 4rem;
        font-weight: 950;
        line-height: 1.1;
        margin-bottom: 20px;
        color: #FFFFFF;
    }

    .hero-sub {
        color: #B7C2D2;
        font-size: 1.25rem;
        line-height: 1.7;
    }
    
    .note-title {
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 8px;
        color: #FFFFFF;
    }

    .note-text {
        font-size: 1.15rem;
        line-height: 1.7;
        color: #B7C2D2;
    }

    .section-title {
    font-size: 1.8rem;
    font-weight: 800;
    margin-top: 20px;
    margin-bottom: 10px;
    color: #EAF2FF;
    letter-spacing: 0.5px;
    }

    .sidebar-header {
        background: linear-gradient(135deg, rgba(18, 26, 45, 0.95), rgba(10, 15, 28, 0.95));
        padding: 20px 18px;
        border-radius: 16px;
        margin-bottom: 18px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .sidebar-kicker {
        font-size: 0.85rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #7CCBFF;
        margin-bottom: 6px;
        font-weight: 700;
    }

    .sidebar-title {
        font-size: 1.4rem;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 8px;
    }

    .sidebar-sub {
        font-size: 1.05rem;
        color: #A8B3C7;
        line-height: 1.6;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(20, 28, 45, 0.98) 0%, rgba(10, 14, 24, 0.98) 100%);
        border-radius: 24px;
        padding: 30px;
        min-height: 190px;
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.3);
        border-left: 4px solid transparent;
    }

    .metric-card.positive { border-left: 4px solid #6DF7AD; }
    .metric-card.negative { border-left: 4px solid #FF6B6B; }
    .metric-card.warning { border-left: 4px solid #FFD166; }
    .metric-card.neutral { border-left: 4px solid #7CCBFF; }

    .metric-value {
        font-size: 3rem;
        font-weight: 950;
    }

    .metric-card.positive .metric-value { color: #6DF7AD; }
    .metric-card.negative .metric-value { color: #FF6B6B; }
    .metric-card.warning .metric-value { color: #FFD166; }
    .metric-card.neutral .metric-value { color: #7CCBFF; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.04);
        border-radius: 999px 999px 0 0;
        padding: 0.7rem 1.2rem;
        border: 1px solid rgba(255,255,255,0.08);
        border-bottom: none;
        font-weight: 700;
        font-size: 1rem;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(76, 201, 240, 0.25), rgba(109, 247, 173, 0.2));
        border-color: rgba(124, 203, 255, 0.4);
        box-shadow: 0 -2px 10px rgba(76, 201, 240, 0.2);
    }

    div[data-testid="stDataFrame"] table {
        font-size: 1.1rem !important;
        background: rgba(15,22,37,0.9);
    }

    div[data-testid="stDataFrame"] th {
        font-weight: 800 !important;
        padding: 14px !important;
    }

    div[data-testid="stDataFrame"] td {
        padding: 14px !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================

def normalize_symbol(symbol):
    return str(symbol).replace(".NS", "").strip()


@st.cache_data(show_spinner=False)
def load_stocks():
    return pd.read_csv("data/nse_stocks.csv")


@st.cache_data(show_spinner=False)
def load_price_history(symbol, period):
    data = yf.download(
        f"{symbol}.NS",
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False,
    )

    if data.empty or "Close" not in data:
        return pd.Series(dtype=float, name=symbol)

    close = data["Close"]

    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    close = close.dropna()
    close.name = symbol
    return close


@st.cache_data(show_spinner=False)
def build_price_frame(symbols, period):
    frames = []
    missing = []

    for symbol in symbols:
        series = load_price_history(symbol, period)
        if series.empty:
            missing.append(symbol)
        else:
            frames.append(series)

    if not frames:
        raise ValueError("No data available for the selected stocks.")

    df = pd.concat(frames, axis=1, join="outer").sort_index()
    df = df.dropna(axis=1, how="all")
    df = df.ffill().bfill()

    return df, missing


def metric_card(title, value, subtitle="", tone="neutral"):
    subtitle_html = f"<div class='metric-sub'>{html_lib.escape(subtitle)}</div>" if subtitle else ""
    return f'<div class="metric-card {tone}"><div class="metric-label">{html_lib.escape(title)}</div><div class="metric-value">{html_lib.escape(value)}</div>{subtitle_html}</div>'


def render_metric_row(cards):
    cols = st.columns(len(cards), gap="medium")
    for col, card in zip(cols, cards):
        with col:
            st.markdown(card, unsafe_allow_html=True)


def info_box(title, text, accent="#7CCBFF"):
    safe_title = html_lib.escape(title)
    safe_text = html_lib.escape(text).replace("\n", "<br>")
    return f"""
    <div class="note-box" style="border-left-color: {accent};">
        <div class="note-title">{safe_title}</div>
        <div class="note-text">{safe_text}</div>
    </div>
    """


# ============================================================
# LOAD STOCK MASTER LIST
# ============================================================

try:
    stocks_df = load_stocks()
except FileNotFoundError:
    st.error("nse_stocks.csv was not found in the project root.")
    st.stop()

stock_options = {
    f"{row['NAME OF COMPANY']} ({row['SYMBOL']})": row["SYMBOL"]
    for _, row in stocks_df.iterrows()
}

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Portfolio Analytics Dashboard</div>
        <div class="hero-sub">
            Decompose performance, systematic risk, and allocation across your holdings. 
            Inputs are benchmarked against the NIFTY 50 to compute relative alpha and historical drawdown.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR INPUTS
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-header">
            <div class="sidebar-kicker">INPUT</div>
            <div class="sidebar-title">Build your portfolio</div>
            <div class="sidebar-sub">Search stocks, choose the period, and enter capital for each selected stock.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_display = st.multiselect(
        "Select Stocks",
        options=list(stock_options.keys()),
        placeholder="Type to search stocks...",
    )

    selected_stocks = [stock_options[item] for item in selected_display]

    period = st.selectbox(
        "Select Period",
        ["3mo", "6mo", "1y", "3y", "5y"],
        index=2,
    )

    st.markdown("### Investment Amounts")

    amounts = []
    for stock in selected_stocks:
        amt = st.number_input(
            f"Amount for {stock}",
            min_value=0.0,
            step=100.0,
            value=0.0,
            format="%.0f",
            key=f"amt_{stock}",
        )
        amounts.append(amt)

    analyze = st.button("Analyze Portfolio", use_container_width=True)

    st.markdown(
        """
        <div class="sidebar-foot">
            Historical series are loaded stock-by-stock and merged to keep the selected window continuous.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# INITIAL STATE
# ============================================================

if not analyze:
    st.markdown(
        info_box(
            "Ready to analyze",
            "Select one or more stocks in the sidebar, enter amounts, and press Analyze Portfolio.",
            accent="#6DF7AD",
        ),
        unsafe_allow_html=True,
    )
    st.stop()

# ============================================================
# VALIDATION
# ============================================================

if not selected_stocks:
    st.warning("Please select at least one stock.")
    st.stop()

if sum(amounts) <= 0:
    st.warning("Please enter investment amounts greater than zero.")
    st.stop()

# ============================================================
# BACKEND
# ============================================================

with st.spinner("Loading historical data and calculating metrics..."):
    df, missing_prices = build_price_frame(tuple(selected_stocks), period)

    if df.empty:
        st.error("No usable historical data was returned for the selected stocks.")
        st.stop()

    available_stocks = list(df.columns)

    amount_map = dict(zip(selected_stocks, amounts))
    selected_stocks = available_stocks
    amounts = [amount_map.get(symbol, 0) for symbol in available_stocks]

    if missing_prices:
        st.warning(f"Historical data unavailable for: {', '.join(missing_prices)}")

    weights = np.array(amounts, dtype=float) / sum(amounts)

    returns = compute_returns(df)
    portfolio_returns = portfolio_return(returns, weights)

    if portfolio_returns.empty:
        st.error("Portfolio returns could not be computed from the selected data.")
        st.stop()

    end_date = df.index.max()
    start_date = df.index.min()

    benchmark_end = end_date + pd.Timedelta(days=1)
    nifty_data = yf.download(
        "^NSEI",
        start=start_date,
        end=benchmark_end,
        interval="1d",
        auto_adjust=True,
        progress=False,
    )

    if nifty_data.empty or "Close" not in nifty_data:
        st.error("Unable to fetch benchmark data.")
        st.stop()

    nifty_close = nifty_data["Close"]

    if isinstance(nifty_close, pd.DataFrame):
        nifty_close = nifty_close.iloc[:, 0]

    nifty_close = nifty_close.dropna()

    if nifty_close.empty:
        st.error("Unable to fetch benchmark data.")
        st.stop()

    nifty_returns = nifty_close.pct_change().dropna()

    common_index = portfolio_returns.index.intersection(nifty_returns.index)

    if common_index.empty:
        st.error("No overlapping dates were found between portfolio and benchmark data.")
        st.stop()

    portfolio_returns = portfolio_returns.loc[common_index]
    nifty_returns = nifty_returns.loc[common_index]

    vol = portfolio_volatility(portfolio_returns)
    risk = classify_risk(vol)
    drawdown = max_drawdown(portfolio_returns)
    sharpe = sharpe_ratio(portfolio_returns)

    cumulative = (1 + portfolio_returns).cumprod()
    port_return = float((cumulative.iloc[-1] - 1) * 100)

    nifty_cum = (1 + nifty_returns).cumprod()
    nifty_return = float((nifty_cum.iloc[-1] - 1) * 100)

    alpha = float(port_return - nifty_return)

    if len(returns.columns) > 1:
        avg_corr = diversification_score(returns)
        diversification = classify_diversification(avg_corr)
        diversification_subtitle = f"Average correlation: {avg_corr:.2f}"
    else:
        avg_corr = np.nan
        diversification = "N/A"
        diversification_subtitle = "Requires at least 2 stocks"

    best, worst, contribution = contribution_analysis(returns, weights)

    latest_prices_ns = pd.Series({f"{k}.NS": v for k, v in df.iloc[-1].items()})
    div_yields, avg_div_yield = portfolio_dividend_yield(
        selected_stocks,
        period,
        weights,
        start_date=start_date,
        prices=latest_prices_ns,
    )

    sector_map, sector_data, missing_sector = sector_breakdown(selected_stocks, weights)

    tech_rows = []
    for col in df.columns:
        signal, _, _, rsi, ma20, ma50 = technical_signal(df[col])

        if ma20 > ma50:
            trend_label = "Bullish"
        elif ma20 < ma50:
            trend_label = "Bearish"
        else:
            trend_label = "Neutral"

        if rsi > 70:
            rsi_label = "Overbought"
        elif rsi < 30:
            rsi_label = "Oversold"
        else:
            rsi_label = "Neutral"

        tech_rows.append(
            {
                "Stock": normalize_symbol(col),
                "MA20": ma20,
                "MA50": ma50,
                "Trend (MA20 vs MA50)": trend_label,
                "RSI": rsi,
                "RSI State": rsi_label,
                "Signal": signal,
            }
        )

    tech_df = pd.DataFrame(tech_rows)

# ============================================================
# CONTEXT
# ============================================================

st.markdown(
    info_box(
        "Portfolio context",
        f"Stocks: {', '.join(selected_stocks)}\nPeriod: {period}\nData window: {start_date.date()} to {end_date.date()}",
        accent="#7CCBFF",
    ),
    unsafe_allow_html=True,
)

if missing_sector:
    st.caption(f"Sector data not available for: {', '.join(missing_sector)}")

# ============================================================
# OVERVIEW
# ============================================================

st.markdown("<div class='section-title'>Overview</div>", unsafe_allow_html=True)

cards = [
    metric_card(
        "Portfolio Return",
        f"{port_return:+.2f}%",
        "Cumulative return of the selected basket",
        "positive" if port_return >= 0 else "negative",
    ),
    metric_card(
        "NIFTY 50 Return",
        f"{nifty_return:+.2f}%",
        "Benchmark return over the same dates",
        "positive" if nifty_return >= 0 else "negative",
    ),
    metric_card(
        "Alpha",
        f"{alpha:+.2f}%",
        "Portfolio return minus NIFTY return",
        "positive" if alpha >= 0 else "negative",
    ),
    metric_card(
        "Risk",
        risk,
        f"Annualized volatility: {vol:.2%}",
        "warning",
    ),
    metric_card(
        "Sharpe Ratio",
        f"{sharpe:.2f}",
        "Return per unit of risk",
        "positive" if sharpe >= 1 else "warning" if sharpe >= 0.5 else "negative",
    ),
    metric_card(
        "Drawdown",
        f"{drawdown:.2%}",
        "Largest peak-to-trough fall",
        "negative",
    ),
    metric_card(
        "Diversification",
        diversification,
        diversification_subtitle,
        "positive" if diversification == "Good" else "warning" if diversification == "Moderate" else "negative",
    ),
    metric_card(
        "Dividend Yield",
        f"{avg_div_yield * 100:.2f}%",
        "Weighted historical dividend yield",
        "positive" if avg_div_yield > 0 else "neutral",
    ),
]

render_metric_row(cards[:4])
st.markdown("<div style='height: 0.35rem;'></div>", unsafe_allow_html=True)
render_metric_row(cards[4:])

st.markdown(
    info_box(
        "Metric guide",
        "Return is the total percentage change over the selected period. Alpha is the portfolio return minus the benchmark return. Sharpe shows return relative to volatility. Drawdown is the maximum fall from a previous peak. Diversification is based on average correlation across the selected stocks.",
        accent="#FFD166",
    ),
    unsafe_allow_html=True,
)

# ============================================================
# ANALYSIS TABS
# ============================================================

st.markdown("<div class='section-title'>Analysis</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "Performance",
        "Correlation",
        "Allocation",
        "Contribution",
        "Risk",
        "Technical",
        "Fundamentals",
    ]
)

# ============================================================
# PERFORMANCE TAB
# ============================================================

with tab1:
    st.plotly_chart(portfolio_growth(portfolio_returns), use_container_width=True)
    st.markdown(
        info_box(
            "How to read",
            "The line shows how ₹1 invested in the selected portfolio grows over time. Values above 1 mean gains; values below 1 mean losses. The chart is rebased to the first day in the selected window.",
            accent="#6DF7AD",
        ),
        unsafe_allow_html=True,
    )

# ============================================================
# CORRELATION TAB
# ============================================================

with tab2:
    st.plotly_chart(correlation_heatmap(returns), use_container_width=True)
    st.markdown(
        info_box(
            "How to read",
            "Correlation is calculated from daily returns. Values close to +1 mean two stocks move together, values near 0 mean weak relation, and values close to -1 mean they move in opposite directions.",
            accent="#7CCBFF",
        ),
        unsafe_allow_html=True,
    )

# ============================================================
# ALLOCATION TAB
# ============================================================

with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(allocation_pie_chart(weights, selected_stocks), use_container_width=True)

    with col2:
        st.plotly_chart(sector_allocation_pie(selected_stocks, weights), use_container_width=True)

    st.markdown(
        info_box(
            "How to read",
            "The stock allocation pie shows how capital is split across the selected stocks. The sector allocation pie groups the same capital by sector, so you can see concentration across industries.",
            accent="#B788FF",
        ),
        unsafe_allow_html=True,
    )

# ============================================================
# CONTRIBUTION TAB
# ============================================================

with tab4:
    st.plotly_chart(contribution_chart(returns.columns, contribution), use_container_width=True)

    contribution_df = pd.DataFrame(
        {
            "Stock": [normalize_symbol(x) for x in returns.columns],
            "Contribution": contribution,
        }
    )
    contribution_df = contribution_df.sort_values("Contribution", ascending=False)
    contribution_df["Contribution"] = contribution_df["Contribution"].apply(lambda x: f"{x*100:.2f}%")

    st.dataframe(contribution_df, use_container_width=True, hide_index=True)

    st.markdown(
        info_box(
            "How to read",
            "Positive bars indicate stocks that added to portfolio return. Negative bars indicate stocks that reduced it. These are contribution estimates based on the selected weighting model, so they are used for relative impact rather than exact decomposition.",
            accent="#FF9F1C",
        ),
        unsafe_allow_html=True,
    )

# ============================================================
# RISK TAB
# ============================================================

with tab5:
    st.plotly_chart(risk_return_scatter(returns), use_container_width=True)
    st.markdown(
        info_box(
            "How to read",
            "Each point is one stock. Moving right means higher volatility (more risk). Moving up means higher annualized return. The upper-right area represents stronger return for the level of risk taken.",
            accent="#FFD166",
        ),
        unsafe_allow_html=True,
    )

# ============================================================
# TECHNICAL TAB
# ============================================================

with tab6:
    st.dataframe(tech_df, use_container_width=True, hide_index=True)

    st.markdown(
        info_box(
            "How to read",
            "MA20 and MA50 are moving averages. Trend is derived from MA20 versus MA50: MA20 above MA50 is Bullish, MA20 below MA50 is Bearish, and near equal is Neutral. RSI below 30 is Oversold, 30 to 70 is Neutral, and above 70 is Overbought. Signal is the technical model output.",
            accent="#9D7CFF",
        ),
        unsafe_allow_html=True,
    )

    with st.expander("Indicator guide"):
        st.markdown(
            """
            - MA20: short-term moving average
            - MA50: medium-term moving average
            - RSI: momentum indicator
            - Signal: combined technical output
            """
        )

# ============================================================
# FUNDAMENTALS TAB
# ============================================================

with tab7:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='subsection-title'>Dividend Yield</div>", unsafe_allow_html=True)
        dividend_rows = [
            {"Stock": stock, "Dividend Yield": f"{value * 100:.2f}%"}
            for stock, value in sorted(div_yields.items(), key=lambda item: item[1], reverse=True)
        ]
        dividend_df = pd.DataFrame(dividend_rows)

        if dividend_df.empty:
            st.info("No dividend data available for the selected stocks.")
        else:
            st.dataframe(dividend_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("<div class='subsection-title'>Sector Breakdown</div>", unsafe_allow_html=True)
        sector_rows = [
            {
                "Sector": sector,
                "Weight": f"{value * 100:.2f}%",
                "Stocks": ", ".join(sector_map[sector]),
            }
            for sector, value in sorted(sector_data.items(), key=lambda item: item[1], reverse=True)
        ]
        sector_df = pd.DataFrame(sector_rows)

        if sector_df.empty:
            st.info("No sector data available for the selected stocks.")
        else:
            st.dataframe(sector_df, use_container_width=True, hide_index=True)

    st.markdown(
        info_box(
            "How to read",
            "Dividend yield shows historical dividend payments relative to the latest available price. Sector breakdown groups your selected stocks by industry and shows how much capital is exposed to each sector.",
            accent="#6DF7AD",
        ),
        unsafe_allow_html=True,
    )