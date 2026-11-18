
from argon2 import PasswordHasher
from argon2.exceptions import (
    HashingError,
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

# Use Argon2id with the library's secure default parameters.
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")

    try:
        return password_hasher.hash(password)
    except HashingError as exc:
        raise RuntimeError("Password hashing failed.") from exc


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a plaintext password against its stored Argon2id hash."""
    if not isinstance(password_hash, str) or not isinstance(password, str):
        return False

    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    """Check whether a stored hash should be upgraded."""
    if not isinstance(password_hash, str) or not password_hash:
        return False

    try:
        return password_hasher.check_needs_rehash(password_hash)
    except (VerificationError, InvalidHashError):
        return False