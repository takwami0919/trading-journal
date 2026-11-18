from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.trade import Trade

router = APIRouter(prefix="/trades", tags=["Trades"])


# GET ALL TRADES
@router.get("/")
def get_trades():
    with SessionLocal() as db:
        trades = db.scalars(
            select(Trade).order_by(Trade.entry_time.desc())
        ).all()

        return [
            {
                "id": str(trade.id),
                "symbol": trade.symbol,
                "direction": trade.direction,
                "status": trade.status,
                "quantity": trade.quantity,
                "remaining_quantity": trade.remaining_quantity,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "gross_pnl": trade.gross_pnl,
                "net_pnl": trade.net_pnl,
                "fees": trade.fees,
                "entry_time": trade.entry_time,
                "exit_time": trade.exit_time,
            }
            for trade in trades
        ]


# GET ONE TRADE BY ID
@router.get("/{trade_id}")
def get_trade(trade_id: UUID):
    with SessionLocal() as db:
        trade = db.get(Trade, trade_id)

        if trade is None:
            raise HTTPException(
                status_code=404,
                detail="Trade not found"
            )

        return {
            "id": str(trade.id),
            "symbol": trade.symbol,
            "direction": trade.direction,
            "status": trade.status,
            "quantity": trade.quantity,
            "remaining_quantity": trade.remaining_quantity,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "gross_pnl": trade.gross_pnl,
            "net_pnl": trade.net_pnl,
            "fees": trade.fees,
            "entry_time": trade.entry_time,
            "exit_time": trade.exit_time,
        }