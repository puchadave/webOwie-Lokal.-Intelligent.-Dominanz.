from cryptography.fernet import Fernet
import os

# Utility to manage token encryption/decryption using Fernet symmetric keys.
# Production: supply ADS_ENCRYPTION_KEY via environment or a secrets manager.


def get_fernet_from_env():
    key = os.environ.get('ADS_ENCRYPTION_KEY')
    if not key:
        return None
    try:
        return Fernet(key)
    except Exception:
        return None


def encrypt_bytes(data: bytes) -> bytes:
    f = get_fernet_from_env()
    if not f:
        # if no key provided, return data as-is (no encryption)
        return data
    return f.encrypt(data)


def decrypt_bytes(data: bytes) -> bytes:
    f = get_fernet_from_env()
    if not f:
        return data
    return f.decrypt(data)
