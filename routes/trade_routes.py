"""Trade synchronization API (Phase 7).

Flow:  get broker account -> connect MT5 -> fetch trades
       -> check duplicate ticket -> store new trades -> return count
"""
from flask import Blueprint, jsonify

from models import BrokerAccount, Trade
from utils.db import db
from services.mt5_service import get_mt5_service, MT5ConnectionError

trade_bp = Blueprint("trades", __name__)


def sync_trades_for_account(account_id):
    """Sync trades for one broker account. Returns count of NEW trades stored.

    Reusable by both the API route and the background worker.
    Raises LookupError if the account is missing, MT5ConnectionError on connect failure.
    """
    account = BrokerAccount.query.get(account_id)
    if not account:
        raise LookupError("Broker account not found")

    mt5 = get_mt5_service()
    mt5.connect(account)  # may raise MT5ConnectionError
    fetched = mt5.fetch_trades(account)

    new_count = 0
    for t in fetched:
        # Duplicate prevention: skip silently if this ticket already exists
        if Trade.query.filter_by(ticket=t["ticket"]).first():
            continue

        trade = Trade(
            ticket=t["ticket"],
            account_id=account.id,
            symbol=t.get("symbol"),
            volume=t.get("volume"),
            profit=t.get("profit"),
            open_time=t.get("open_time"),
            close_time=t.get("close_time"),
        )
        db.session.add(trade)
        new_count += 1

    db.session.commit()
    return new_count


@trade_bp.route("/sync-trades/<int:account_id>", methods=["POST"])
def sync_trades(account_id):
    try:
        synced = sync_trades_for_account(account_id)
    except LookupError:
        return jsonify({"error": "Broker account not found"}), 404
    except MT5ConnectionError:
        return jsonify({"error": "Unable to connect MT5"}), 502

    return jsonify({"synced_trades": synced})
