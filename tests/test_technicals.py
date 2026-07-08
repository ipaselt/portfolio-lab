"""Indicator math tests — synthetic series with hand-checkable outcomes, no network."""
import pandas as pd
import pytest

from src.research.technicals import relative_strength, rsi, sma


def test_sma_basic():
    close = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    out = sma(close, 3)
    assert pd.isna(out.iloc[1])
    assert out.iloc[2] == 2.0
    assert out.iloc[4] == 4.0


def test_rsi_all_gains_is_100():
    close = pd.Series(range(1, 40), dtype=float)  # monotonic up
    out = rsi(close, 14)
    assert out.iloc[-1] == pytest.approx(100.0)


def test_rsi_all_losses_is_0():
    close = pd.Series(range(40, 1, -1), dtype=float)  # monotonic down
    out = rsi(close, 14)
    assert out.iloc[-1] == pytest.approx(0.0)


def test_rsi_warmup_is_nan():
    close = pd.Series(range(1, 40), dtype=float)
    out = rsi(close, 14)
    assert out.iloc[:13].isna().all()


def test_rsi_flat_series_bounded():
    # Alternating +1/-1 → gains equal losses → RSI near 50.
    values = [100.0]
    for i in range(60):
        values.append(values[-1] + (1 if i % 2 == 0 else -1))
    out = rsi(pd.Series(values), 14)
    assert 40 < out.iloc[-1] < 60


def test_relative_strength_outperformance():
    idx = pd.date_range("2026-01-01", periods=4)
    ticker = pd.Series([100, 110, 121, 133.1], index=idx)     # +10%/period
    bench = pd.Series([100, 105, 110.25, 115.76], index=idx)  # +5%/period
    out = relative_strength(ticker, bench)
    assert out.iloc[0] == pytest.approx(1.0)
    assert out.iloc[-1] == pytest.approx(1.331 / 1.1576, rel=1e-3)


def test_relative_strength_aligns_dates():
    ticker = pd.Series([100, 110, 120], index=pd.date_range("2026-01-01", periods=3))
    bench = pd.Series([50, 55], index=pd.date_range("2026-01-02", periods=2))
    out = relative_strength(ticker, bench)
    # Only the two overlapping dates survive; both rebased to their first shared date.
    assert len(out) == 2
    assert out.iloc[0] == pytest.approx(1.0)
