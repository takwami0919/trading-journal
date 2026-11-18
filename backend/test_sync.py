
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, func

import app.models
from app.core.database import SessionLocal
from app.models.broker_connection import BrokerConnection
from app.models.execution import Execution
from app.services.execution_sync import save_executions


def test_sync():
    # Create a unique fake fill for this test
    fake_fill = {
        "id": f"test-{uuid.uuid4()}",
        "symbol": "AAPL",
        "side": "buy",
        "qty": "5",
        "price": "200.50",
        "transaction_time": datetime.now(timezone.utc).isoformat(),
    }

    with SessionLocal() as db:
        connection = db.scalar(
            select(BrokerConnection).where(
                BrokerConnection.broker_name == "alpaca"
            )
        )

        if connection is None:
            raise RuntimeError("Alpaca connection not found.")

        # Save the same fill twice
        first = save_executions(db, connection.id, [fake_fill])
        second = save_executions(db, connection.id, [fake_fill])

        count = db.scalar(
            select(func.count()).select_from(Execution).where(
                Execution.broker_connection_id == connection.id,
                Execution.broker_execution_id == fake_fill["id"],
            )
        )

        print("First insert:", first)
        print("Second insert:", second)
        print("Matching database rows:", count)

        assert first == 1
        assert second == 0
        assert count == 1

        # Remove the synthetic test record
        record = db.scalar(
            select(Execution).where(
                Execution.broker_connection_id == connection.id,
                Execution.broker_execution_id == fake_fill["id"],
            )
        )
        db.delete(record)
        db.commit()

        print("Test passed. Fake execution removed.")


if __name__ == "__main__":
    test_sync()
