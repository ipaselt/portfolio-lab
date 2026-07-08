"""Watchlist persistence tests — use a tmp dir so the user's real data/ is untouched."""
import src.watchlist as wl


def _use_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(wl, "WATCHLIST_PATH", tmp_path / "watchlist.json")


def test_add_dedupes_and_uppercases(tmp_path, monkeypatch):
    _use_tmp(tmp_path, monkeypatch)
    wl.add_ticker("msft")
    wl.add_ticker("MSFT")
    wl.add_ticker(" googl ")
    assert wl.load_watchlist() == ["GOOGL", "MSFT"]


def test_remove(tmp_path, monkeypatch):
    _use_tmp(tmp_path, monkeypatch)
    wl.add_ticker("MSFT")
    wl.add_ticker("GOOGL")
    wl.remove_ticker("msft")
    assert wl.load_watchlist() == ["GOOGL"]


def test_load_empty_when_no_file(tmp_path, monkeypatch):
    _use_tmp(tmp_path, monkeypatch)
    assert wl.load_watchlist() == []
