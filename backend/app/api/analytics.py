
from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.trade import Trade

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# Dashboard summary statistics
@router.get("/summary")
def get_analytics_summary():
    with SessionLocal() as db:
        trades = db.scalars(select(Trade)).all()

        closed_trades = [
            trade for trade in trades
            if trade.status == "closed"
        ]

        winning_trades = [
            trade for trade in closed_trades
            if trade.net_pnl is not None
            and trade.net_pnl > 0
        ]

        losing_trades = [
            trade for trade in closed_trades
            if trade.net_pnl is not None
            and trade.net_pnl < 0
        ]

        total_pnl = sum(
            (
                Decimal(str(trade.net_pnl))
                for trade in closed_trades
                if trade.net_pnl is not None
            ),
            Decimal("0")
        )

        win_rate = (
            len(winning_trades) / len(closed_trades) * 100
            if closed_trades else 0
        )

        return {
            "total_trades": len(trades),
            "open_trades": len(trades) - len(closed_trades),
            "closed_trades": len(closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "total_realized_pnl": float(total_pnl),
            "win_rate": round(win_rate, 2),
        }


# Cumulative realized P&L chart
@router.get("/performance")
def get_performance():
    with SessionLocal() as db:
        closed_trades = db.scalars(
            select(Trade)
            .where(
                Trade.status == "closed",
                Trade.exit_time.is_not(None)
            )
            .order_by(Trade.exit_time, Trade.id)
        ).all()

        cumulative_pnl = Decimal("0")
        performance = []

        for trade in closed_trades:
            pnl = Decimal(str(trade.net_pnl or 0))
            cumulative_pnl += pnl

            performance.append({
                "date": trade.exit_time.isoformat(),
                "symbol": trade.symbol,
                "trade_pnl": float(pnl),
                "cumulative_pnl": float(cumulative_pnl),
            })

        return performance
