from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()


def hash_password(password):
    """Retourne l'empreinte Argon2id de `password`, à stocker en base."""
    return _hasher.hash(password)


def verify_password(password, password_hash):
    """Retourne True si `password` correspond à l'empreinte `password_hash`, sinon False."""
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


# A tester