"""Verification helpers for authenticated CCSDS command packets."""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import ByteString
from dataclasses import dataclass


@dataclass(frozen=True)
class HMACVerifier:
    """Verify HMAC-SHA256 signatures for incoming command packets."""

    key: bytes

    def verify(self, message: ByteString, signature: ByteString) -> bool:
        """Return True if the signature matches the provided message."""
        expected = hmac.new(self.key, bytes(message), hashlib.sha256).digest()
        return hmac.compare_digest(expected, bytes(signature))


__all__ = ["HMACVerifier"]
