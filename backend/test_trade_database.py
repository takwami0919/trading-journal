
from sqlalchemy import select, func
from decimal import Decimal
import app.models
from app.core.database import SessionLocal
from app.models.trade import Trade, TradeExecution


def test_database_state():
    db = SessionLocal()

    try:
        trades = db.scalars(select(Trade)).all()

        print("Trades in database:", len(trades))

        for trade in trades:
            linked_count = db.scalar(
                select(func.count())
                .select_from(TradeExecution)
                .where(TradeExecution.trade_id == trade.id)
            )

            print("Symbol:", trade.symbol)
            print("Status:", trade.status)
            print("Remaining quantity:", trade.remaining_quantity)
            print("Linked executions:", linked_count)
            print("Trade ID:", trade.id)

        assert len(trades) == 1
        assert trades[0].symbol == "BTC/USD"
        assert trades[0].status == "open"
        assert trades[0].remaining_quantity == Decimal("0.000500")  
        print("DATABASE BASELINE TEST PASSED!")

    finally:
        db.close()


if __name__ == "__main__":
    test_database_state()
