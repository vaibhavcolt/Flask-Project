"""MT5 abstraction layer (Phase 6).

`get_mt5_service()` returns a Mock implementation by default so the project
runs with zero MT5 credentials. Set MT5_MODE=real (Windows + MetaTrader5
package) to use the live integration.

Every implementation exposes:
    connect(account) -> bool
    fetch_trades(account) -> list[dict]   # ticket, symbol, volume, profit, open_time, close_time
"""
from datetime import datetime, timedelta

from flask import current_app


class MT5ConnectionError(Exception):
    """Raised when we cannot connect to MT5."""


class BaseMT5Service:
    def connect(self, account):
        raise NotImplementedError

    def fetch_trades(self, account):
        raise NotImplementedError


class MockMT5Service(BaseMT5Service):
    """Version 1 – fake trades, no credentials required.

    Trades are derived deterministically from the account id, so re-syncing
    the same account returns the *same* tickets. That lets the duplicate-
    prevention logic be observed: first sync inserts N, the next inserts 0.
    """

    def connect(self, account):
        # A real connection could fail; the mock always succeeds.
        return True

    def fetch_trades(self, account):
        base = int(account.id) * 1000
        now = datetime.utcnow()
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        trades = []
        for i in range(3):
            ticket = str(base + i + 1)
            trades.append(
                {
                    "ticket": ticket,
                    "symbol": symbols[i % len(symbols)],
                    "volume": round(0.5 * (i + 1), 2),  # 0.5, 1.0, 1.5
                    "profit": 50 * (i + 1),
                    "open_time": now - timedelta(hours=i + 1),
                    "close_time": now - timedelta(minutes=(i + 1) * 10),
                }
            )
        return trades


class RealMT5Service(BaseMT5Service):
    """Version 2 – live MetaTrader5 (Windows only)."""

    def connect(self, account):
        try:
            import MetaTrader5 as mt5  # noqa: N813
        except ImportError as exc:  # pragma: no cover - platform dependent
            raise MT5ConnectionError("MetaTrader5 package not installed") from exc

        ok = mt5.initialize(
            login=int(account.account_number),
            password=account.password,
            server=account.server,
        )
        if not ok:
            raise MT5ConnectionError("Unable to connect MT5")
        return True

    def fetch_trades(self, account):
        import MetaTrader5 as mt5  # noqa: N813

        deals = mt5.history_deals_get() or []
        trades = []
        for d in deals:
            trades.append(
                {
                    "ticket": str(d.ticket),
                    "symbol": d.symbol,
                    "volume": d.volume,
                    "profit": d.profit,
                    "open_time": datetime.fromtimestamp(d.time),
                    "close_time": datetime.fromtimestamp(d.time),
                }
            )
        return trades


def get_mt5_service():
    mode = current_app.config.get("MT5_MODE", "mock")
    return RealMT5Service() if mode == "real" else MockMT5Service()
