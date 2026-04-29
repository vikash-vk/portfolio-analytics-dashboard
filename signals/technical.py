# ============================================================
# TECHNICAL
# ============================================================


# =========================
# RSI
# =========================
def compute_rsi(series, window=14):
    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


# =========================
# TECHNICAL SIGNAL
# =========================
def technical_signal(series):
    price = series.iloc[-1]

    ma20 = series.rolling(20).mean().iloc[-1]
    ma50 = series.rolling(50).mean().iloc[-1]

    rsi = compute_rsi(series).iloc[-1]

    if ma20 > ma50 and price > ma50:
        trend = "Bullish"
    elif ma20 < ma50 and price < ma50:
        trend = "Bearish"
    else:
        trend = "Transition"

    if rsi > 70:
        momentum = "Overbought"
    elif rsi < 30:
        momentum = "Oversold"
    else:
        momentum = "Neutral"

    if trend == "Bullish" and momentum == "Neutral":
        signal = "Favorable"
    elif trend == "Bearish" and momentum == "Neutral":
        signal = "Weak"
    elif momentum == "Overbought":
        signal = "Caution"
    elif momentum == "Oversold":
        signal = "Opportunity"
    else:
        signal = "Neutral"

    return signal, trend, momentum, rsi, ma20, ma50