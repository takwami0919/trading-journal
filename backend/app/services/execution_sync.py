
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.adapters.alpaca import AlpacaAdapter
from app.core.config import settings
from app.core.crypto import decrypt_value
from app.models.broker_connection import BrokerConnection
from app.models.execution import Execution


def sync_executions(db: Session, connection_id):
    """Fetch executions and inspect crypto fees from Alpaca."""

    connection = db.scalar(
        select(BrokerConnection).where(
            BrokerConnection.id == connection_id,
            BrokerConnection.is_active.is_(True),
            BrokerConnection.broker_name == "alpaca",
        )
    )

    if connection is None:
        raise ValueError("Active Alpaca connection not found.")

    api_key = decrypt_value(connection.encrypted_api_key)
    secret_key = decrypt_value(connection.encrypted_api_secret)

    adapter = AlpacaAdapter(
        api_key=api_key,
        secret_key=secret_key,
        base_url=settings.ALPACA_PAPER_BASE_URL,
    )

    executions = adapter.get_executions()
    print(f"Fetched {len(executions)} executions from Alpaca.")

    save_executions(db, connection.id, executions)

    # Inspect fee activity without modifying the database
    fees = adapter.get_crypto_fees()

    print(f"\nFetched {len(fees)} crypto fee activities:")
    for fee in fees:
        print({
            "id": fee.get("id"),
            "date": fee.get("date"),
            "symbol": fee.get("symbol"),
            "qty": fee.get("qty"),
            "net_amount": fee.get("net_amount"),
            "description": fee.get("description"),
        })

    return executions


def normalize_execution(fill: dict, connection_id):
    """Convert an Alpaca fill to the database format."""

    return {
        "broker_connection_id": connection_id,
        "broker_execution_id": str(fill["id"]),
        "symbol": fill["symbol"],
        "side": fill["side"].lower(),
        "quantity": Decimal(str(fill["qty"])),
        "price": Decimal(str(fill["price"])),
        "fee": Decimal("0"),
        "executed_at": datetime.fromisoformat(
            fill["transaction_time"].replace("Z", "+00:00")
        ),
        "raw_payload": fill,
    }


def save_executions(db: Session, connection_id, fills: list[dict]) -> int:
    """Insert new fills and refresh existing ones without duplicates."""

    processed = 0

    for fill in fills:
        data = normalize_execution(fill, connection_id)

        stmt = insert(Execution).values(**data)

        stmt = stmt.on_conflict_do_update(
            constraint="uq_execution_per_broker",
            set_={
                "symbol": stmt.excluded.symbol,
                "side": stmt.excluded.side,
                "quantity": stmt.excluded.quantity,
                "price": stmt.excluded.price,
                "executed_at": stmt.excluded.executed_at,
                "raw_payload": stmt.excluded.raw_payload,
            },
        )

        db.execute(stmt)
        processed += 1

    db.commit()

    print(f"Processed {processed} Alpaca executions.")
    return processed
