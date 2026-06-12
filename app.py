"""Application factory + entrypoint (Phase 1).

Run with:  python app.py
"""
from flask import Flask, jsonify

from config import Config
from utils.db import db
from sockets.socket_events import socketio

# Import models so create_all() registers every table.
import models  # noqa: F401
from routes.user_routes import user_bp
from routes.broker_routes import broker_bp
from routes.trade_routes import trade_bp
from routes.commission_routes import commission_bp
from live_data.market_feed import start_market_feed
from workers.sync_worker import start_scheduler


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    socketio.init_app(app)

    # Register API blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(broker_bp)
    app.register_blueprint(trade_bp)
    app.register_blueprint(commission_bp)

    @app.route("/")
    def health():
        return jsonify({"status": "ok", "service": "trading-crm"})

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    # Live market data broadcaster (Phase 11)
    start_market_feed(app.config["MARKET_FEED_INTERVAL_SECONDS"])
    # Periodic sync + commission worker (Phase 13)
    start_scheduler(app, app.config["SYNC_INTERVAL_SECONDS"])

    # socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)


    # For prod
    port = int(os.environ.get("PORT", 5000))
    
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False
        )
