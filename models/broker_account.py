from datetime import datetime

from utils.db import db


class BrokerAccount(db.Model):
    __tablename__ = "broker_accounts"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    account_number = db.Column(db.String(50), nullable=False)
    server = db.Column(db.String(100))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trades = db.relationship(
        "Trade", backref="broker_account", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_number": self.account_number,
            "server": self.server,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
