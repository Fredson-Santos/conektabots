"""Crypto Service — Encryption/Decryption Helpers.

Handles encryption and decryption of sensitive fields.
Uses Python encryption (Fernet) for database-agnostic encryption.
"""

from typing import Optional
import os
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import Fernet
import hashlib
from base64 import urlsafe_b64encode


class CryptoService:
    """Encryption/Decryption for sensitive fields."""

    def __init__(self, session: AsyncSession):
        """Initialize crypto service.

        Args:
            session: Database session
        """
        self.session = session
        self.db_key = os.getenv("DB_ENCRYPTION_KEY", "default-key-32-chars-minimum!")
        self.cipher = self._get_cipher()

    def _get_cipher(self):
        """Get Fernet cipher from key.
        
        Derives a key from the configured encryption key using SHA256.
        """
        # Ensure key is 32+ characters
        if len(self.db_key) < 32:
            key = self.db_key + "0" * (32 - len(self.db_key))
        else:
            key = self.db_key[:32]
        
        # Derive encryption key using SHA256
        key_hash = hashlib.sha256(key.encode()).digest()
        
        # Create Fernet cipher
        key_b64 = urlsafe_b64encode(key_hash)
        return Fernet(key_b64)

    async def encrypt(self, plaintext: Optional[str]) -> Optional[bytes]:
        """Encrypt plaintext using Fernet.

        Args:
            plaintext: Text to encrypt

        Returns:
            Encrypted bytes
        """
        if not plaintext:
            return None

        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return encrypted
        except Exception:
            return None

    async def decrypt(self, ciphertext: Optional[bytes]) -> Optional[str]:
        """Decrypt ciphertext using Fernet.

        Args:
            ciphertext: Encrypted bytes

        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return None

        try:
            decrypted = self.cipher.decrypt(ciphertext)
            return decrypted.decode()
        except Exception:
            return None

    async def encrypt_multiple(self, plaintexts: dict[str, str]) -> dict[str, bytes]:
        """Encrypt multiple fields at once.

        Args:
            plaintexts: Dict of {field_name: plaintext_value}

        Returns:
            Dict of {field_name: encrypted_bytes}
        """
        encrypted = {}
        for field_name, plaintext in plaintexts.items():
            if plaintext:
                encrypted[field_name] = await self.encrypt(plaintext)
            else:
                encrypted[field_name] = None
        return encrypted

    async def decrypt_multiple(self, ciphertexts: dict[str, bytes]) -> dict[str, str]:
        """Decrypt multiple fields at once.

        Args:
            ciphertexts: Dict of {field_name: encrypted_bytes}

        Returns:
            Dict of {field_name: plaintext}
        """
        decrypted = {}
        for field_name, ciphertext in ciphertexts.items():
            if ciphertext:
                decrypted[field_name] = await self.decrypt(ciphertext)
            else:
                decrypted[field_name] = None
        return decrypted
