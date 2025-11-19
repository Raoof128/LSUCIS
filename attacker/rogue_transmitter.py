"""Rogue transmitter attempting to spoof CCSDS command traffic."""

from __future__ import annotations

import argparse
import os
import socket

from ccsds.packet_builder import CCSDSPacketBuilder

DEFAULT_ENDPOINT: tuple[str, int] = ("127.0.0.1", 5000)


class RogueTransmitter:
    """Craft spoofed, malformed, or replayed packets to attack the satellite bus."""

    def __init__(self, endpoint: tuple[str, int]) -> None:
        """Store the configured target endpoint for packet transmission."""
        self.endpoint = endpoint

    def send_raw(self, payload: bytes) -> None:
        """Send the provided bytes directly to the configured endpoint."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload, self.endpoint)

    def spoof_command(self, command: str, ground_id: str) -> None:
        """Send a structurally valid packet with an incorrect HMAC key."""
        # Deliberately use the wrong key so the HMAC fails
        builder = CCSDSPacketBuilder(key=os.urandom(32))
        packet = builder.build(command, ground_id)
        self.send_raw(packet)

    def send_malformed(self) -> None:
        """Transmit random binary data that should fail CCSDS parsing."""
        junk = os.urandom(24)
        self.send_raw(junk)

    def replay(self, packet: bytes) -> None:
        """Replay a captured packet byte-for-byte."""
        self.send_raw(packet)


def parse_args() -> argparse.Namespace:
    """Return parsed CLI arguments for executing rogue transmissions."""
    parser = argparse.ArgumentParser(description="Attempt to spoof the satellite bus")
    parser.add_argument("--host", default=DEFAULT_ENDPOINT[0], help="Satellite IP address")
    parser.add_argument("--port", type=int, default=DEFAULT_ENDPOINT[1], help="Satellite UDP port")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    spoof = subparsers.add_parser("spoof", help="Send a spoofed but structurally valid packet")
    spoof.add_argument("command", help="Command string to spoof, e.g. 'CMD: SHUTDOWN_THRUSTERS'")
    spoof.add_argument("--ground-id", default="GS-ALPHA", help="Ground ID to impersonate")

    subparsers.add_parser("malformed", help="Send binary junk that should fail parsing")

    replay = subparsers.add_parser(
        "replay", help="Replay a hex-encoded packet captured on the wire"
    )
    replay.add_argument("packet_hex", help="Hex string representing a full packet")

    return parser.parse_args()


def main() -> None:
    """Entry point for launching rogue transmission modes."""
    args = parse_args()
    transmitter = RogueTransmitter(endpoint=(args.host, args.port))

    if args.mode == "spoof":
        transmitter.spoof_command(args.command, args.ground_id)
    elif args.mode == "malformed":
        transmitter.send_malformed()
    elif args.mode == "replay":
        transmitter.replay(bytes.fromhex(args.packet_hex))


if __name__ == "__main__":
    main()
