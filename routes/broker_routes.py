"""Broker account APIs (Phase 5)."""
from flask import Blueprint, request, jsonify

from models import User, BrokerAccount
from utils.db import db

broker_bp = Blueprint("broker_accounts", __name__)


@broker_bp.route("/broker-accounts", methods=["POST"])
def add_broker_account():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    account_number = data.get("account_number")

    if not user_id or not account_number:
        return jsonify({"error": "user_id and account_number are required"}), 400

    if not User.query.get(user_id):
        return jsonify({"error": "User not found"}), 404

    account = BrokerAccount(
        user_id=user_id,
        account_number=account_number,
        server=data.get("server"),
        password=data.get("password"),
    )
    db.session.add(account)
    db.session.commit()

    return jsonify({"message": "Broker account added", "id": account.id}), 201


@broker_bp.route("/broker-accounts", methods=["GET"])
def list_broker_accounts():
    accounts = BrokerAccount.query.order_by(BrokerAccount.id).all()
    return jsonify([a.to_dict() for a in accounts])
