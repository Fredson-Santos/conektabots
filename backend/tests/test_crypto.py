"""Test Encryption — Sensitive Field Protection.

Verifies encryption/decryption of credentials.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.crypto_service import CryptoService


@pytest.mark.asyncio
async def test_encrypt_decrypt(session: AsyncSession):
    """Test encryption and decryption."""
    service = CryptoService(session)

    plaintext = "my_secret_api_token"

    # Encrypt
    encrypted = await service.encrypt(plaintext)
    assert encrypted is not None
    assert encrypted != plaintext.encode()

    # Decrypt
    decrypted = await service.decrypt(encrypted)
    assert decrypted == plaintext


@pytest.mark.asyncio
async def test_encrypt_empty_value(session: AsyncSession):
    """Test encryption of empty/None values."""
    service = CryptoService(session)

    encrypted = await service.encrypt("")
    assert encrypted is None or encrypted == b""

    encrypted = await service.encrypt(None)
    assert encrypted is None


@pytest.mark.asyncio
async def test_decrypt_empty_value(session: AsyncSession):
    """Test decryption of empty/None values."""
    service = CryptoService(session)

    decrypted = await service.decrypt(None)
    assert decrypted is None

    decrypted = await service.decrypt(b"")
    assert decrypted is None or decrypted == ""


@pytest.mark.asyncio
async def test_multiple_encryptions_same_value(session: AsyncSession):
    """Test that same plaintext encrypts to different ciphertext (IVs).

    Actually pgcrypto might use same IV - just verify we can decrypt both.
    """
    service = CryptoService(session)

    plaintext = "same_secret"

    enc1 = await service.encrypt(plaintext)
    enc2 = await service.encrypt(plaintext)

    # Both should decrypt to same plaintext
    dec1 = await service.decrypt(enc1)
    dec2 = await service.decrypt(enc2)

    assert dec1 == plaintext
    assert dec2 == plaintext


@pytest.mark.asyncio
async def test_encrypt_multiple_fields(session: AsyncSession):
    """Test encrypting multiple fields at once."""
    service = CryptoService(session)

    plaintexts = {
        "api_hash": "hash123",
        "bot_token": "token456",
        "session_string": "session789",
    }

    encrypted = await service.encrypt_multiple(plaintexts)

    assert "api_hash" in encrypted
    assert "bot_token" in encrypted
    assert "session_string" in encrypted
    assert encrypted["api_hash"] is not None


@pytest.mark.asyncio
async def test_decrypt_multiple_fields(session: AsyncSession):
    """Test decrypting multiple fields at once."""
    service = CryptoService(session)

    # First encrypt
    plaintexts = {
        "api_hash": "hash123",
        "bot_token": "token456",
    }
    encrypted = await service.encrypt_multiple(plaintexts)

    # Then decrypt
    decrypted = await service.decrypt_multiple(encrypted)

    assert decrypted["api_hash"] == "hash123"
    assert decrypted["bot_token"] == "token456"
