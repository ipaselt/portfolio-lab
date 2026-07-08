"""Technical indicators over yfinance price history. Pure pandas — no TA library dependency.

Research aid, not a trading signal generator. Indicators here are the standard textbook
formulations: simple moving averages, Wilder-smoothed RSI, and relative strength as the ratio of
cumulative returns vs. a benchmark.
"""
import pandas as pd
import yfinance as yf


def fetch_history(ticker, period="1y", interval="1d"):
    """OHLCV DataFrame for a ticker. Raises ValueError when Yahoo has nothing for the symbol."""
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No price history for {ticker!r} — check the symbol.")
    return df


def sma(close, window):
    """Simple moving average of a close series."""
    return close.rolling(window).mean()


def rsi(close, window=14):
    """Relative Strength Index, Wilder smoothing (the standard 14-period formulation)."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    # avg_loss of 0 (all gains) makes RS inf → RSI resolves to exactly 100; the first
    # `window` rows stay NaN (warm-up), which the chart simply doesn't draw.
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def relative_strength(close, benchmark_close):
    """Cumulative-return ratio vs. a benchmark, rebased to 1.0 at the first shared date.

    > 1 means the ticker has outperformed the benchmark since the window start.
    """
    joined = pd.concat({"t": close, "b": benchmark_close}, axis=1).dropna()
    t_rebased = joined["t"] / joined["t"].iloc[0]
    b_rebased = joined["b"] / joined["b"].iloc[0]
    return t_rebased / b_rebased
