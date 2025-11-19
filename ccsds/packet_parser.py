"""CCSDS packet parsing helpers for the satellite bus."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from datetime import UTC, datetime

from ccsdspy import PacketField

from crypto.constants import HMAC_DIGEST_LENGTH

# Keep field definitions in sync with packet_builder to demonstrate ccsdspy usage.
PRIMARY_HEADER_FIELDS = [
    PacketField("CCSDS_VERSION_NUMBER", "uint", 3),
    PacketField("CCSDS_PACKET_TYPE", "uint", 1),
    PacketField("CCSDS_SECONDARY_FLAG", "uint", 1),
    PacketField("CCSDS_APID", "uint", 11),
    PacketField("CCSDS_SEQUENCE_FLAG", "uint", 2),
    PacketField("CCSDS_SEQUENCE_COUNT", "uint", 14),
    PacketField("CCSDS_PACKET_LENGTH", "uint", 16),
]

SECONDARY_HEADER_FIELDS = [
    PacketField("TIMESTAMP", "uint", 64),
    PacketField("GROUND_STATION_ID_LENGTH", "uint", 16),
]

PAYLOAD_FIELDS = [PacketField("COMMAND_LENGTH", "uint", 16)]


@dataclass
class ParsedPacket:
    """Structured view of a decoded CCSDS packet."""

    command: str
    ground_station_id: str
    timestamp: datetime
    sequence_count: int
    apid: int
    raw_without_signature: bytes
    signature: bytes


class PacketValidationError(Exception):
    """Raised when a packet cannot be decoded or fails validation."""


class CCSDSPacketParser:
    """Parse and validate CCSDS command packets as defined in packet_builder."""

    signature_length = HMAC_DIGEST_LENGTH

    def parse(self, packet: bytes) -> ParsedPacket:
        """Decode a CCSDS packet into its constituent headers and payload."""
        if len(packet) < 6 + self.signature_length:
            raise PacketValidationError("Packet too short to contain CCSDS header and signature")

        primary_header = packet[:6]
        first_word, second_word, packet_length = struct.unpack(">HHH", primary_header)
        version = (first_word >> 13) & 0x7
        packet_type = (first_word >> 12) & 0x1
        secondary_header_flag = (first_word >> 11) & 0x1
        apid = first_word & 0x7FF
        sequence_flags = (second_word >> 14) & 0x3
        sequence_count = second_word & 0x3FFF

        if version != 0 or packet_type != 1 or secondary_header_flag != 1:
            raise PacketValidationError("Unsupported CCSDS header values")
        if sequence_flags != 3:
            raise PacketValidationError("Fragmented packets are not supported in this simulator")

        expected_total_length = packet_length + 1 + 6
        if expected_total_length != len(packet):
            raise PacketValidationError(
                "Packet length mismatch. Expected "
                f"{expected_total_length} bytes, received {len(packet)}"
            )

        data_field = packet[6:]
        signature = data_field[-self.signature_length :]
        secondary_and_payload = data_field[: -self.signature_length]

        if len(secondary_and_payload) < 10:
            raise PacketValidationError("Secondary header missing or truncated")

        timestamp_seconds, ground_station_id_length = struct.unpack(
            ">QH", secondary_and_payload[:10]
        )
        ground_station_end = 10 + ground_station_id_length
        if ground_station_end > len(secondary_and_payload):
            raise PacketValidationError("Ground station identifier is incomplete")

        ground_station_id = secondary_and_payload[10:ground_station_end].decode("utf-8")
        if len(secondary_and_payload) < ground_station_end + 2:
            raise PacketValidationError("Payload command length missing")

        command_length = struct.unpack(
            ">H", secondary_and_payload[ground_station_end : ground_station_end + 2]
        )[0]
        payload_start = ground_station_end + 2
        payload_end = payload_start + command_length
        if payload_end > len(secondary_and_payload):
            raise PacketValidationError("Payload command bytes truncated")

        command = secondary_and_payload[payload_start:payload_end].decode("utf-8")
        raw_without_signature = packet[: -self.signature_length]

        timestamp = datetime.fromtimestamp(timestamp_seconds, tz=UTC)
        return ParsedPacket(
            command=command,
            ground_station_id=ground_station_id,
            timestamp=timestamp,
            sequence_count=sequence_count,
            apid=apid,
            raw_without_signature=raw_without_signature,
            signature=signature,
        )


__all__ = [
    "CCSDSPacketParser",
    "ParsedPacket",
    "PacketValidationError",
    "PRIMARY_HEADER_FIELDS",
    "SECONDARY_HEADER_FIELDS",
    "PAYLOAD_FIELDS",
]
