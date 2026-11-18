
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.config import settings
from app.core.crypto import decrypt_value

from app.adapters.alpaca import AlpacaAdapter

from app.models.execution import Execution
from app.models.broker_connection import BrokerConnection

from app.services.execution_sync import sync_executions
from app.services.trade_persistence import (
    save_open_trades,
    save_closed_trades,
)

router = APIRouter(
    prefix="/executions",
    tags=["Executions"]
)


# GET ALL EXECUTIONS
@router.get("/")
def get_executions():
    with SessionLocal() as db:
        executions = db.scalars(
            select(Execution).order_by(
                Execution.executed_at.desc()
            )
        ).all()

        return [
            {
                "id": str(execution.id),
                "symbol": execution.symbol,
                "side": execution.side,
                "quantity": execution.quantity,
                "price": execution.price,
                "fee": execution.fee,
                "executed_at": execution.executed_at,
                "broker_execution_id": execution.broker_execution_id,
            }
            for execution in executions
        ]


# GET CURRENT ALPACA POSITIONS
@router.get("/positions")
def get_alpaca_positions():
    with SessionLocal() as db:
        connection = db.scalar(
            select(BrokerConnection).where(
                BrokerConnection.broker_name == "alpaca",
                BrokerConnection.is_active.is_(True),
            )
        )

        if connection is None:
            raise HTTPException(
                status_code=404,
                detail="No active Alpaca connection found.",
            )

        try:
            adapter = AlpacaAdapter(
                api_key=decrypt_value(
                    connection.encrypted_api_key
                ),
                secret_key=decrypt_value(
                    connection.encrypted_api_secret
                ),
                base_url=settings.ALPACA_PAPER_BASE_URL,
            )

            return adapter.get_positions()

        except Exception:
            raise HTTPException(
                status_code=502,
                detail="Could not retrieve Alpaca positions.",
            )


# IMPORT ALPACA EXECUTIONS AND UPDATE TRADES
@router.post("/sync")
def sync_alpaca_executions():
    with SessionLocal() as db:

        connection = db.scalar(
            select(BrokerConnection).where(
                BrokerConnection.broker_name == "alpaca",
                BrokerConnection.is_active.is_(True),
            )
        )

        if connection is None:
            raise HTTPException(
                status_code=404,
                detail="No active Alpaca connection found.",
            )

        try:
            # Fetch executions from Alpaca
            executions = sync_executions(
                db,
                connection.id
            )

            # Create or update open trades
            open_trades = save_open_trades(
                db,
                connection.user_id
            )

            # Create or update closed trades
            closed_trades = save_closed_trades(
                db,
                connection.user_id
            )

        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=502,
                detail=(
                    "Alpaca synchronization failed. "
                    "Check backend terminal logs."
                ),
            )

        return {
            "message": "Alpaca synchronization completed successfully.",
            "fetched_executions": len(executions),
            "open_trades_processed": open_trades,
            "closed_trades_processed": closed_trades,
        }
