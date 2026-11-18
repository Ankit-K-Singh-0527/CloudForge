import pytest

from app.services.password_service import (
    hash_password,
    verify_password,
)


def test_hash_password_returns_argon2id_hash():
    password_hash = hash_password("CloudForge-Secure-Password-2026")

    assert password_hash.startswith("$argon2id$")


def test_verify_password_accepts_correct_password():
    password = "CloudForge-Secure-Password-2026"
    password_hash = hash_password(password)

    assert verify_password(password_hash, password) is True


def test_verify_password_rejects_incorrect_password():
    password_hash = hash_password("CloudForge-Secure-Password-2026")

    assert verify_password(password_hash, "Incorrect-Password") is False


def test_verify_password_rejects_malformed_hash():
    assert verify_password("invalid-hash", "Some-Password") is False

def test_hash_password_rejects_empty_password():
    with pytest.raises(ValueError):
        hash_password("")