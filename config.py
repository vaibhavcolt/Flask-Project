"""Application configuration.

All values can be overridden through environment variables so the same code
runs locally and in CI/containers without edits.
"""
import os


class Config:
    # --- MySQL connection -------------------------------------------------
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "trading_crm")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'trading_crm.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # --- MT5 -------------------------------------------------------------
    # "mock" (default, no credentials needed) or "real" (Windows + MetaTrader5)
    MT5_MODE = os.getenv("MT5_MODE", "mock")

    # --- Commission engine ----------------------------------------------
    COMMISSION_PER_LOT = float(os.getenv("COMMISSION_PER_LOT", "5"))

    # --- Background worker ----------------------------------------------
    # APScheduler interval in seconds (assignment: "every minute")
    SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", "60"))

    # Broadcast fake market data every N seconds
    MARKET_FEED_INTERVAL_SECONDS = int(os.getenv("MARKET_FEED_INTERVAL_SECONDS", "1"))
