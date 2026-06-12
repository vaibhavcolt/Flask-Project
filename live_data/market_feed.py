"""Live market data feed (Phase 11).

Generates fake prices and broadcasts a `market_data` event every second.
Each symbol is emitted to its own room so clients only receive the symbols
they `subscribe`d to (see sockets/socket_events.py).
"""
import random

from sockets.socket_events import socketio

SYMBOLS = {
    "EURUSD": 1.0850,
    "GBPUSD": 1.2700,
    "USDJPY": 157.20,
}


def _next_price(base):
    # small random walk around the base price
    return round(base + random.uniform(-0.0020, 0.0020) * base, 4)


def market_feed_loop(interval_seconds=1):
    while True:
        for symbol, base in SYMBOLS.items():
            payload = {"symbol": symbol, "price": _next_price(base)}
            # broadcast to the room named after the symbol
            socketio.emit("market_data", payload, to=symbol)
        socketio.sleep(interval_seconds)


def start_market_feed(interval_seconds=1):
    """Launch the feed as a Socket.IO background task."""
    socketio.start_background_task(market_feed_loop, interval_seconds)
