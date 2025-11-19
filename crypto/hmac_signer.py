"""Utilities for generating HMAC-SHA256 signatures for uplink commands."""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import ByteString
from dataclasses import dataclass


@dataclass(frozen=True)
class HMACSigner:
    """
    Simple wrapper around HMAC-SHA256 signing.

    The signer is intentionally small so it can be reused by both the ground
    station and the satellite side without pulling in additional dependencies.
    """

    key: bytes

    def sign(self, message: ByteString) -> bytes:
        """Return the raw HMAC-SHA256 signature for the provided message."""
        digest = hmac.new(self.key, bytes(message), hashlib.sha256).digest()
        return digest

    def hexdigest(self, message: ByteString) -> str:
        """Return the hexadecimal representation of the signature."""
        return hmac.new(self.key, bytes(message), hashlib.sha256).hexdigest()


__all__ = ["HMACSigner"]
