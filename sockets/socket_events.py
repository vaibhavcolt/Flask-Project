"""Socket.IO instance and event handlers.

Phase 10 / Phase 11:
  - clients can `subscribe` to one or more symbols (joins a room per symbol)
  - the market feed broadcasts `market_data` to each symbol's room
  - the commission engine emits `commission_created`
"""
from flask_socketio import SocketIO, join_room, leave_room

# threading async mode keeps the setup dependency-free (no eventlet/gevent)
# and plays nicely with APScheduler's background thread.
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")


@socketio.on("connect")
def handle_connect():
    print("[socket] client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("[socket] client disconnected")


@socketio.on("subscribe")
def handle_subscribe(data):
    """Subscribe a client to live market data for given symbol(s).

    Payload: {"symbols": ["EURUSD", "GBPUSD"]}  or  {"symbol": "EURUSD"}
    """
    symbols = _extract_symbols(data)
    for symbol in symbols:
        join_room(symbol)
    return {"subscribed": symbols}


@socketio.on("unsubscribe")
def handle_unsubscribe(data):
    symbols = _extract_symbols(data)
    for symbol in symbols:
        leave_room(symbol)
    return {"unsubscribed": symbols}


def _extract_symbols(data):
    if not isinstance(data, dict):
        return []
    if data.get("symbols"):
        return list(data["symbols"])
    if data.get("symbol"):
        return [data["symbol"]]
    return []
