"""Firewall logic for the satellite command bus."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ccsds.packet_parser import CCSDSPacketParser, PacketValidationError, ParsedPacket
from crypto.verifier import HMACVerifier
from satellite.telemetry import TelemetryLogger


@dataclass
class FirewallDecision:
    """Outcome of firewall inspection for a single packet."""

    accepted: bool
    reason: str
    packet: ParsedPacket | None = None


class SatelliteFirewall:
    """Validate CCSDS command packets using HMAC and ground station allow-lists."""

    def __init__(
        self, key: bytes, allowed_ground_stations: Iterable[str], telemetry: TelemetryLogger
    ) -> None:
        """Configure signature verification, allow list, and telemetry handlers."""
        self.verifier = HMACVerifier(key)
        self.allowed_ground_stations: set[str] = set(allowed_ground_stations)
        self.parser = CCSDSPacketParser()
        self.telemetry = telemetry

    def inspect(self, packet: bytes, source_ip: str) -> FirewallDecision:
        """Parse, validate, and authorize an incoming packet."""
        try:
            parsed = self.parser.parse(packet)
        except PacketValidationError as exc:
            self.telemetry.warning(
                "Packet Decode Failure",
                source_ip=source_ip,
                error=str(exc),
            )
            return FirewallDecision(False, str(exc))

        if parsed.ground_station_id not in self.allowed_ground_stations:
            reason = "Ground station ID not authorized"
            self.telemetry.critical(
                "CRITICAL SECURITY ALERT: Unauthorized ground station",
                source_ip=source_ip,
                ground_station_id=parsed.ground_station_id,
                reason=reason,
                command=parsed.command,
            )
            return FirewallDecision(False, reason, parsed)

        if not self.verifier.verify(parsed.raw_without_signature, parsed.signature):
            reason = "HMAC verification failed"
            self.telemetry.critical(
                "CRITICAL SECURITY ALERT: Uplink Spoof Attempt Detected",
                source_ip=source_ip,
                ground_station_id=parsed.ground_station_id,
                command=parsed.command,
                reason=reason,
            )
            return FirewallDecision(False, reason, parsed)

        self.telemetry.info(
            "Command accepted",
            source_ip=source_ip,
            command=parsed.command,
            ground_station_id=parsed.ground_station_id,
            sequence=parsed.sequence_count,
        )
        return FirewallDecision(True, "Command accepted", parsed)


__all__ = ["SatelliteFirewall", "FirewallDecision"]
