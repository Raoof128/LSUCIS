"""CCSDS command packet generation using ccsdspy field definitions."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from datetime import UTC, datetime

from ccsdspy import PacketField

from crypto.constants import HMAC_DIGEST_LENGTH
from crypto.hmac_signer import HMACSigner

PRIMARY_HEADER_FIELDS: list[PacketField] = [
    PacketField("CCSDS_VERSION_NUMBER", "uint", 3),
    PacketField("CCSDS_PACKET_TYPE", "uint", 1),
    PacketField("CCSDS_SECONDARY_FLAG", "uint", 1),
    PacketField("CCSDS_APID", "uint", 11),
    PacketField("CCSDS_SEQUENCE_FLAG", "uint", 2),
    PacketField("CCSDS_SEQUENCE_COUNT", "uint", 14),
    PacketField("CCSDS_PACKET_LENGTH", "uint", 16),
]

SECONDARY_HEADER_FIELDS: list[PacketField] = [
    PacketField("TIMESTAMP", "uint", 64),
    PacketField("GROUND_STATION_ID_LENGTH", "uint", 16),
]

PAYLOAD_FIELDS: list[PacketField] = [
    PacketField("COMMAND_LENGTH", "uint", 16),
]


@dataclass
class CommandMetadata:
    """Metadata captured in every generated CCSDS command packet."""

    command: str
    ground_station_id: str
    sequence_count: int
    apid: int
    timestamp: datetime


class CCSDSPacketBuilder:
    """Build CCSDS-like command packets and sign them with HMAC-SHA256."""

    def __init__(self, key: bytes, apid: int = 100) -> None:
        """Initialize the builder with a shared secret and application ID."""
        self.signer = HMACSigner(key)
        self.apid = apid
        self.sequence_count = 0

    def build(self, command: str, ground_station_id: str) -> bytes:
        """Create a fully signed CCSDS packet ready for transmission."""
        timestamp = datetime.now(tz=UTC)
        secondary_header = self._build_secondary_header(timestamp, ground_station_id)
        payload = self._build_payload(command)

        pre_signature = secondary_header + payload
        packet_length = len(pre_signature) + HMAC_DIGEST_LENGTH - 1

        primary_header = self._build_primary_header(packet_length)
        unsigned_packet = primary_header + pre_signature
        signature = self.signer.sign(unsigned_packet)
        full_packet = unsigned_packet + signature

        self.sequence_count = (self.sequence_count + 1) % 16384
        return full_packet

    def describe(self, command: str, ground_station_id: str) -> CommandMetadata:
        """Return the metadata that will be embedded in the next packet."""
        return CommandMetadata(
            command=command,
            ground_station_id=ground_station_id,
            sequence_count=self.sequence_count,
            apid=self.apid,
            timestamp=datetime.now(tz=UTC),
        )

    def _build_primary_header(self, packet_length: int) -> bytes:
        """Construct the CCSDS primary header for the next packet."""
        version_number = 0
        packet_type = 1  # command
        secondary_header_flag = 1
        sequence_flags = 3  # stand-alone packet

        first_two_bytes = (
            (version_number & 0x7) << 13
            | (packet_type & 0x1) << 12
            | (secondary_header_flag & 0x1) << 11
            | (self.apid & 0x7FF)
        )
        next_two_bytes = ((sequence_flags & 0x3) << 14) | (self.sequence_count & 0x3FFF)

        primary_header = struct.pack(
            ">HHH",
            first_two_bytes,
            next_two_bytes,
            packet_length & 0xFFFF,
        )
        return primary_header

    def _build_secondary_header(self, timestamp: datetime, ground_station_id: str) -> bytes:
        """Encode the secondary header with timestamp and ground station ID."""
        ts_seconds = int(timestamp.timestamp())
        ground_station_bytes = ground_station_id.encode("utf-8")
        return struct.pack(">QH", ts_seconds, len(ground_station_bytes)) + ground_station_bytes

    def _build_payload(self, command: str) -> bytes:
        """Encode the command payload with a length prefix."""
        command_bytes = command.encode("utf-8")
        return struct.pack(">H", len(command_bytes)) + command_bytes


def asdict(metadata: CommandMetadata) -> dict[str, str]:
    """Return a dictionary representation of metadata for logging."""
    return {
        "command": metadata.command,
        "ground_station_id": metadata.ground_station_id,
        "sequence_count": str(metadata.sequence_count),
        "apid": str(metadata.apid),
        "timestamp": metadata.timestamp.isoformat(),
    }


__all__ = [
    "CCSDSPacketBuilder",
    "CommandMetadata",
    "PRIMARY_HEADER_FIELDS",
    "SECONDARY_HEADER_FIELDS",
    "PAYLOAD_FIELDS",
    "asdict",
]
