"""
Importing this package registers every model on Base.metadata, which is
what Alembic's `--autogenerate` inspects to build migrations. Whenever you
add a new model file, import it here too.
"""
from app.models.broker_connection import BrokerConnection
from app.models.daily_performance import DailyPerformance
from app.models.execution import Execution
from app.models.journal import Screenshot, Strategy, TradeNote
from app.models.trade import Trade, TradeExecution
from app.models.user import User

__all__ = [
    "User",
    "BrokerConnection",
    "Execution",
    "Trade",
    "TradeExecution",
    "Strategy",
    "TradeNote",
    "Screenshot",
    "DailyPerformance",
]
