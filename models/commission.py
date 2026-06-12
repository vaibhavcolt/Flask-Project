from datetime import datetime

from utils.db import db


class Commission(db.Model):
    __tablename__ = "commissions"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    # one commission per trade -> unique guards against double-charging on re-runs
    trade_id = db.Column(db.BigInteger, db.ForeignKey("trades.id"), unique=True, nullable=False)
    commission_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "trade_id": self.trade_id,
            "commission_amount": self.commission_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
