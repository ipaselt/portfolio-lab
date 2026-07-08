"""Format tests for the fundamentals module — no network needed."""
from src.research.fundamentals import format_value


def test_margin_fields_are_fractions():
    assert format_value("Net margin", 0.393) == "39.3%"


def test_dividend_yield_is_already_percent():
    # yfinance quirk verified live 2026-07-08: dividendYield comes pre-multiplied (2.52 = 2.52%),
    # unlike margins/growth. A KO yield of 2.52 must NOT render as 252%.
    assert format_value("Dividend yield", 2.52) == "2.52%"


def test_big_dollar_abbreviation():
    assert format_value("Market cap", 4.94e12) == "$4.94T"
    assert format_value("Free cash flow", 46.34e9) == "$46.34B"


def test_none_renders_as_dash():
    assert format_value("P/E (ttm)", None) == "—"


def test_ratio_format():
    assert format_value("P/E (ttm)", 31.23) == "31.2x"
