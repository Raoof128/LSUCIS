"""
Shared cryptographic constants for uplink authentication.

This module centralizes values such as the HMAC digest length so packet
builders and parsers remain aligned without relying on magic numbers.
"""

from __future__ import annotations

from hashlib import sha256

HMAC_DIGEST_LENGTH = sha256().digest_size

__all__ = ["HMAC_DIGEST_LENGTH"]
