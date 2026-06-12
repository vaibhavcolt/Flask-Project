"""Commission API (Phase 9)."""
from flask import Blueprint, jsonify

from models import BrokerAccount
from services.commission_service import calculate_commissions_for_account

commission_bp = Blueprint("commissions", __name__)


@commission_bp.route("/calculate-commission/<int:account_id>", methods=["POST"])
def calculate_commission_route(account_id):
    if not BrokerAccount.query.get(account_id):
        return jsonify({"error": "Broker account not found"}), 404

    created = calculate_commissions_for_account(account_id)
    return jsonify({"commissions_created": created})
