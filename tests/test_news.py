"""News helper tests — no network."""
from datetime import datetime, timedelta, timezone

from src.research.news import age_label


def test_age_label_minutes():
    ts = datetime.now(timezone.utc) - timedelta(minutes=30)
    assert age_label(ts).endswith("m ago")


def test_age_label_hours():
    ts = datetime.now(timezone.utc) - timedelta(hours=5)
    assert age_label(ts) == "5h ago"


def test_age_label_days():
    ts = datetime.now(timezone.utc) - timedelta(days=3, hours=2)
    assert age_label(ts) == "3d ago"


def test_age_label_none():
    assert age_label(None) == ""
