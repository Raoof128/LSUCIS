"""Shared helpers for resolving cryptographic secrets securely."""

from __future__ import annotations

import os

DEMO_KEY = b"CHANGE_ME_DEMO_KEY"


def resolve_hmac_key(
    cli_key: str | None,
    *,
    env_var: str = "SATCOM_KEY",
    allow_demo_fallback: bool = True,
) -> tuple[bytes, bool]:
    """
    Return the HMAC key bytes and whether a demo fallback was used.

    A CLI-provided key takes priority, followed by an environment variable. The optional
    demo fallback keeps local demos simple while signalling to callers whether the
    returned secret is production-ready.

    Parameters
    ----------
    cli_key: str | None
        Explicit key provided via CLI flag. If present, this value is always used.
    env_var: str
        Environment variable name to check for a configured key. Defaults to
        ``SATCOM_KEY``.
    allow_demo_fallback: bool
        When ``True``, fall back to a non-secret demo key if no other source is provided.
        When ``False``, a :class:`ValueError` is raised instead.

    Returns
    -------
    tuple[bytes, bool]
        The resolved key bytes and a boolean indicating whether the demo fallback was
        used.

    Raises
    ------
    ValueError
        If no key is supplied and ``allow_demo_fallback`` is ``False``.

    """
    if cli_key:
        return cli_key.encode(), False

    env_value = os.getenv(env_var)
    if env_value:
        return env_value.encode(), False

    if allow_demo_fallback:
        return DEMO_KEY, True

    raise ValueError("HMAC key not provided. Set --key or the SATCOM_KEY environment variable.")


__all__ = ["resolve_hmac_key", "DEMO_KEY"]
