from cryptography.fernet import Fernet
from app.core.config import settings


def get_cipher():
    return Fernet(settings.CREDENTIAL_ENCRYPTION_KEY.encode())


def encrypt_value(value: str) -> str:
    """Encrypt a string before storing it in PostgreSQL."""
    return get_cipher().encrypt(value.encode()).decode()


def decrypt_value(encrypted_value: str) -> str:
    """Decrypt a stored value when communicating with Alpaca."""
    return get_cipher().decrypt(encrypted_value.encode()).decode()