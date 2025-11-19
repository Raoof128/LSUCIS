"""Telemetry logging utilities for the satellite bus."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any


class TelemetryLogger:
    """Structured telemetry logger writing to file and stdout."""

    def __init__(self, path: str = "telemetry.log") -> None:
        """Configure file and stream handlers for structured telemetry output."""
        self.logger = logging.getLogger("telemetry")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%SZ",
            )

            file_handler = logging.FileHandler(path)
            file_handler.setFormatter(formatter)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(stream_handler)

    def emit(self, level: int, message: str, **context: Any) -> None:
        """Emit a structured telemetry event at the given log level."""
        payload: dict[str, Any] = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "message": message,
            **context,
        }
        self.logger.log(level, json.dumps(payload))

    def info(self, message: str, **context: Any) -> None:
        """Record an informational telemetry event."""
        self.emit(logging.INFO, message, **context)

    def warning(self, message: str, **context: Any) -> None:
        """Record a warning telemetry event."""
        self.emit(logging.WARNING, message, **context)

    def critical(self, message: str, **context: Any) -> None:
        """Record a critical telemetry event."""
        self.emit(logging.CRITICAL, message, **context)


__all__ = ["TelemetryLogger"]
