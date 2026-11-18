import secrets

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.crypto import encrypt_value
from app.core.database import SessionLocal
from app.models.user import User
from app.models.broker_connection import BrokerConnection

# Load all model definitions for SQLAlchemy relationships
import app.models
DEMO_EMAIL = "demo@tradingjournal.local"


def setup_demo():
    with SessionLocal() as db:
        # Find the demo user or create one
        user = db.scalar(
            select(User).where(User.email == DEMO_EMAIL)
        )

        if user is None:
            user = User(
                email=DEMO_EMAIL,
                password_hash=secrets.token_hex(32),
            )
            db.add(user)
            db.flush()
            print("Demo user created.")
        else:
            print("Demo user already exists.")

        # Find an existing Alpaca connection
        connection = db.scalar(
            select(BrokerConnection).where(
                BrokerConnection.user_id == user.id,
                BrokerConnection.broker_name == "alpaca",
            )
        )

        if connection is None:
            connection = BrokerConnection(
                user_id=user.id,
                broker_name="alpaca",
                encrypted_api_key=encrypt_value(settings.ALPACA_API_KEY),
                encrypted_api_secret=encrypt_value(settings.ALPACA_SECRET_KEY),
                is_active=True,
            )
            db.add(connection)
            print("Alpaca paper connection created.")
        else:
            # Refresh credentials if paper keys were regenerated
            connection.encrypted_api_key = encrypt_value(
                settings.ALPACA_API_KEY
            )
            connection.encrypted_api_secret = encrypt_value(
                settings.ALPACA_SECRET_KEY
            )
            connection.is_active = True
            print("Existing Alpaca connection updated.")

        db.commit()
        print("Demo setup completed successfully.")


if __name__ == "__main__":
    setup_demo()