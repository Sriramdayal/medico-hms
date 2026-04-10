"""
Medico HMS — Field-Level Encryption Helpers
Application-level encryption for PHI fields using Fernet symmetric encryption.
"""

import base64
import hashlib
import logging

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

logger = logging.getLogger("apps.core.encryption")


def _get_fernet():
    """Get a Fernet instance from the configured encryption key."""
    key = settings.FIELD_ENCRYPTION_KEY
    # Ensure the key is exactly 32 bytes, URL-safe base64 encoded
    if len(key) != 44 or not key.endswith("="):
        # Derive a proper Fernet key from the configured key
        key_bytes = hashlib.sha256(key.encode()).digest()
        key = base64.urlsafe_b64encode(key_bytes).decode()
    return Fernet(key)


def encrypt_value(value):
    """
    Encrypt a string value using Fernet symmetric encryption.

    Args:
        value: The plaintext string to encrypt.

    Returns:
        The encrypted string (base64-encoded), or empty string if input is empty.
    """
    if not value:
        return value

    try:
        f = _get_fernet()
        encrypted = f.encrypt(value.encode("utf-8"))
        return encrypted.decode("utf-8")
    except Exception:
        logger.exception("Encryption failed")
        raise


def decrypt_value(value):
    """
    Decrypt a Fernet-encrypted string.

    Args:
        value: The encrypted string (base64-encoded).

    Returns:
        The decrypted plaintext string.
    """
    if not value:
        return value

    try:
        f = _get_fernet()
        decrypted = f.decrypt(value.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken:
        logger.warning("Failed to decrypt value — may be plaintext or corrupted")
        return value
    except Exception:
        logger.exception("Decryption failed")
        raise


class EncryptedFieldMixin:
    """
    Mixin for Django model fields that transparently encrypts/decrypts values.
    Use with CharField, TextField, etc.

    Usage:
        class Patient(models.Model):
            ssn = EncryptedCharField(max_length=500)

    The value is encrypted before saving and decrypted when reading.
    Note: max_length should account for the encrypted value being larger than plaintext.
    """

    def get_prep_value(self, value):
        """Encrypt value before saving to database."""
        value = super().get_prep_value(value)
        return encrypt_value(value) if value else value

    def from_db_value(self, value, expression, connection):
        """Decrypt value when reading from database."""
        return decrypt_value(value) if value else value


from django.db import models  # noqa: E402


class EncryptedCharField(EncryptedFieldMixin, models.CharField):
    """CharField that transparently encrypts/decrypts its value."""
    pass


class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    """TextField that transparently encrypts/decrypts its value."""
    pass


class EncryptedEmailField(EncryptedFieldMixin, models.EmailField):
    """EmailField that transparently encrypts/decrypts its value."""

    def from_db_value(self, value, expression, connection):
        """Decrypt value when reading from database."""
        return decrypt_value(value) if value else value

    def get_prep_value(self, value):
        """Encrypt value before saving to database."""
        # Skip email validation on encrypted value
        if value:
            return encrypt_value(value)
        return value
