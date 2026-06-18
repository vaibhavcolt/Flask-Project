"""Commission API (Phase 9)."""
from flask import Blueprint, jsonify

from models import BrokerAccount, Commission
from services.commission_service import calculate_commissions_for_account

commission_bp = Blueprint("commissions", __name__)


@commission_bp.route("/calculate-commission/<int:account_id>", methods=["POST"])
def calculate_commission_route(account_id):
    if not BrokerAccount.query.get(account_id):
        return jsonify({"error": "Broker account not found"}), 404

    created = calculate_commissions_for_account(account_id)
    return jsonify({"commissions_created": created})


@commission_bp.route("/commissions", methods=["GET"])
def list_commissions():
    commissions = Commission.query.order_by(Commission.created_at.desc(), Commission.id.desc()).all()
    result = []
    for c in commissions:
        comm_dict = c.to_dict()
        if c.trade:
            comm_dict["ticket"] = c.trade.ticket
            comm_dict["symbol"] = c.trade.symbol
            comm_dict["volume"] = c.trade.volume
            comm_dict["profit"] = c.trade.profit
        result.append(comm_dict)
    return jsonify(result)

