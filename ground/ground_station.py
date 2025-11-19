"""Ground station simulator for generating authenticated CCSDS commands."""

from __future__ import annotations

import argparse
import logging
import socket

from ccsds.packet_builder import CCSDSPacketBuilder
from satellite.telemetry import TelemetryLogger
from utils.secrets import resolve_hmac_key

DEFAULT_GROUND_STATION_ID = "GS-ALPHA"
DEFAULT_SATELLITE_ENDPOINT: tuple[str, int] = ("127.0.0.1", 5000)


class GroundStation:
    """Send signed CCSDS command packets to the satellite bus over UDP."""

    def __init__(self, key: bytes, ground_station_id: str = DEFAULT_GROUND_STATION_ID) -> None:
        """Instantiate a ground station with the provided signing key and identifier."""
        self.builder = CCSDSPacketBuilder(key)
        self.ground_station_id = ground_station_id
        self.telemetry = TelemetryLogger()

    def send(self, command: str, endpoint: tuple[str, int] = DEFAULT_SATELLITE_ENDPOINT) -> None:
        """Generate, sign, and dispatch a command to the configured satellite endpoint."""
        packet = self.builder.build(command, self.ground_station_id)
        metadata = self.builder.describe(command, self.ground_station_id)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(packet, endpoint)
        self.telemetry.info(
            "Command dispatched",
            command=command,
            ground_station_id=self.ground_station_id,
            endpoint=f"{endpoint[0]}:{endpoint[1]}",
            sequence=metadata.sequence_count,
        )


def parse_args() -> argparse.Namespace:
    """Return parsed CLI arguments for dispatching a signed command."""
    parser = argparse.ArgumentParser(description="Send authenticated commands to the satellite bus")
    parser.add_argument("command", help="Command payload, e.g. 'CMD: ORIENT +10'")
    parser.add_argument(
        "--ground-id",
        default=DEFAULT_GROUND_STATION_ID,
        help="Ground station identifier",
    )
    parser.add_argument(
        "--key",
        default=None,
        help="HMAC secret; defaults to SATCOM_KEY env var or built-in demo value",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_SATELLITE_ENDPOINT[0],
        help="Satellite IP address",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_SATELLITE_ENDPOINT[1],
        help="Satellite UDP port",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for sending a single authenticated command."""
    args = parse_args()
    key, used_demo = resolve_hmac_key(args.key)
    if used_demo:
        logging.warning(
            "Using demo HMAC key; set --key or SATCOM_KEY for production-like testing.",
        )
    ground_station = GroundStation(key=key, ground_station_id=args.ground_id)
    ground_station.send(args.command, (args.host, args.port))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
