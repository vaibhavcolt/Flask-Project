"""Commission engine (Phase 8 / 9 / 12).

Formula:  commission = volume * COMMISSION_PER_LOT   (default $5 per lot)
"""
from flask import current_app

from models import Trade, Commission
from utils.db import db
from sockets.socket_events import socketio


def calculate_commission(trade):
    """Pure calculation: $5 per lot traded."""
    rate = current_app.config.get("COMMISSION_PER_LOT", 5)
    return round((trade.volume or 0) * rate, 2)


def calculate_commissions_for_account(account_id):
    """Generate commissions for every trade of an account that doesn't have one yet.

    Flow: get trades -> calculate -> save -> emit `commission_created`.
    Returns the number of commissions created.
    """
    trades = Trade.query.filter_by(account_id=account_id).all()
    created = 0

    for trade in trades:
        # one commission per trade – skip if already calculated
        if Commission.query.filter_by(trade_id=trade.id).first():
            continue

        amount = calculate_commission(trade)
        commission = Commission(trade_id=trade.id, commission_amount=amount)
        db.session.add(commission)
        db.session.commit()
        created += 1

        # Phase 12: notify subscribers in real time
        socketio.emit(
            "commission_created",
            {"trade_id": trade.id, "commission": amount},
        )

    return created
