import os
from cryptography.fernet import Fernet

def _get_fernet():
    # Helper to get fernet at runtime or crash gracefully
    key = os.environ.get("AFIP_FERNET_KEY")
    if not key:
        raise ValueError("AFIP_FERNET_KEY variable de entorno esta vacia o no definida.")
    return Fernet(key)

def encrypt_credential(text: str) -> str:
    fernet = _get_fernet()
    return fernet.encrypt(text.encode()).decode()

def decrypt_credential(encrypted: str) -> str:
    fernet = _get_fernet()
    return fernet.decrypt(encrypted.encode()).decode()
