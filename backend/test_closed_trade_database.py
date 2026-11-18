
import app.models
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select, func
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.models.broker_connection import BrokerConnection
from app.models.execution import Execution
from app.models.trade import Trade
from app.services.trade_persistence import save_closed_trades

# Never run this test against the main database.
assert settings.DATABASE_URL.split("/")[-1].split("?")[0] == "trading_journal_test"

db = SessionLocal()
user_id = None

try:
    # Create a temporary test user.
    user = User(
        email=f"closed-trade-test-{uuid4()}@example.com",
        password_hash="test-only-not-a-real-password-hash",
    )
    db.add(user)
    db.flush()
    user_id = user.id

    # Create a fake broker connection.
    connection = BrokerConnection(
        user_id=user.id,
        broker_name="test",
        encrypted_api_key="fake-test-key",
        encrypted_api_secret="fake-test-secret",
        is_active=False,
    )
    db.add(connection)
    db.flush()

    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    # Buy 10 shares at $100, then sell 10 at $120.
    fills = [
        Execution(
            broker_connection_id=connection.id,
            broker_execution_id=f"test-{uuid4()}",
            symbol="AAPL",
            side=side,
            quantity=Decimal("10"),
            price=Decimal(price),
            fee=Decimal("1"),
            executed_at=start + timedelta(minutes=i),
            raw_payload={},
        )
        for i, (side, price) in enumerate([
            ("buy", "100"),
            ("sell", "120"),
        ])
    ]

    db.add_all(fills)
    db.commit()

    # Save closed trades twice to test duplicate prevention.
    save_closed_trades(db, user_id)
    save_closed_trades(db, user_id)

    trades = db.scalars(
        select(Trade).where(Trade.user_id == user_id)
    ).all()

    assert len(trades) == 1

    trade = trades[0]

    assert trade.status == "closed"
    assert trade.remaining_quantity == Decimal("0")
    assert trade.gross_pnl == Decimal("200")
    assert trade.fees == Decimal("2")
    assert trade.net_pnl == Decimal("198")
    assert len(trade.execution_links) == 2

    print("Closed trades:", len(trades))
    print("Gross P&L:", trade.gross_pnl)
    print("Fees:", trade.fees)
    print("Net P&L:", trade.net_pnl)
    print("CLOSED TRADE DATABASE TEST PASSED!")

finally:
    db.rollback()
    if user_id is not None:
        user = db.get(User, user_id)
        if user is not None:
            db.delete(user)
            db.commit()
    db.close()
