from cryptography.fernet import Fernet
from django.conf import settings

def _get_fernet() -> Fernet:
    key: str = settings.FERNET_KEY
    return Fernet(key.encode())

def encrypt_password(password: str) -> str:
    fernet = _get_fernet()
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    fernet = _get_fernet()
    return fernet.decrypt(encrypted_password.encode()).decode()