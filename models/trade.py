from datetime import datetime

from utils.db import db


class Trade(db.Model):
    __tablename__ = "trades"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    # UNIQUE(ticket) -> prevents duplicate trades on re-sync
    ticket = db.Column(db.String(100), unique=True, nullable=False)
    account_id = db.Column(db.BigInteger, db.ForeignKey("broker_accounts.id"), nullable=False)
    symbol = db.Column(db.String(20))
    volume = db.Column(db.Float)
    profit = db.Column(db.Float)
    open_time = db.Column(db.DateTime)
    close_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    commission = db.relationship(
        "Commission", backref="trade", uselist=False, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "ticket": self.ticket,
            "account_id": self.account_id,
            "symbol": self.symbol,
            "volume": self.volume,
            "profit": self.profit,
            "open_time": self.open_time.isoformat() if self.open_time else None,
            "close_time": self.close_time.isoformat() if self.close_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
