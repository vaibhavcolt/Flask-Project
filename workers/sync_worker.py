"""Background worker (Phase 13).

Every minute (configurable), for each broker account:
    Sync Trades -> Calculate Commissions -> (commission_created events emitted)
"""
from apscheduler.schedulers.background import BackgroundScheduler

from models import BrokerAccount
from routes.trade_routes import sync_trades_for_account
from services.commission_service import calculate_commissions_for_account
from services.mt5_service import MT5ConnectionError


def _run_sync_cycle(app):
    """One full pass over every broker account. Needs an app context for the DB."""
    with app.app_context():
        accounts = BrokerAccount.query.all()
        for account in accounts:
            try:
                synced = sync_trades_for_account(account.id)
                created = calculate_commissions_for_account(account.id)
                print(
                    f"[worker] account={account.id} "
                    f"synced={synced} commissions={created}"
                )
            except MT5ConnectionError:
                print(f"[worker] account={account.id} MT5 connection failed, skipping")
            except Exception as exc:  # keep the scheduler alive on per-account errors
                print(f"[worker] account={account.id} error: {exc}")


def start_scheduler(app, interval_seconds=60):
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        _run_sync_cycle,
        trigger="interval",
        seconds=interval_seconds,
        args=[app],
        id="sync_cycle",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    return scheduler
