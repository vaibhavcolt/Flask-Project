"""User APIs (Phase 4)."""
from flask import Blueprint, request, jsonify

from models import User
from utils.db import db

user_bp = Blueprint("users", __name__)


@user_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created", "id": user.id}), 201


@user_bp.route("/users", methods=["GET"])
def list_users():
    users = User.query.order_by(User.id).all()
    return jsonify([u.to_dict() for u in users])
