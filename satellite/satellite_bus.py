"""Satellite bus listener that validates CCSDS command uplink traffic."""

from __future__ import annotations

import argparse
import logging
import socket
from collections.abc import Iterable

from satellite.firewall import SatelliteFirewall
from satellite.telemetry import TelemetryLogger
from utils.secrets import resolve_hmac_key

DEFAULT_ALLOWED = ("GS-ALPHA",)
DEFAULT_ENDPOINT: tuple[str, int] = ("127.0.0.1", 5000)


class SatelliteBus:
    """UDP-based simulation of a satellite command bus."""

    def __init__(
        self, key: bytes, allowed_ground_ids: Iterable[str], endpoint: tuple[str, int]
    ) -> None:
        """Initialize the UDP listener, firewall, and telemetry emitters."""
        self.telemetry = TelemetryLogger()
        self.firewall = SatelliteFirewall(key, allowed_ground_ids, telemetry=self.telemetry)
        self.endpoint = endpoint

    def run(self) -> None:
        """Start the UDP listener and dispatch packets through the firewall."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(self.endpoint)
            self.telemetry.info(
                "Satellite bus listening",
                endpoint=f"{self.endpoint[0]}:{self.endpoint[1]}",
                allowed_ground_stations=list(self.firewall.allowed_ground_stations),
            )
            while True:
                try:
                    packet, addr = sock.recvfrom(8192)
                    decision = self.firewall.inspect(packet, addr[0])
                    if decision.accepted and decision.packet:
                        self.telemetry.info(
                            "Executing command",
                            command=decision.packet.command,
                            ground_station_id=decision.packet.ground_station_id,
                        )
                except KeyboardInterrupt:
                    self.telemetry.info("Satellite bus shutting down on operator request")
                    break
                except OSError as exc:
                    self.telemetry.critical("Socket error", error=str(exc))
                    break


def parse_args() -> argparse.Namespace:
    """Return parsed CLI arguments for the satellite bus simulator."""
    parser = argparse.ArgumentParser(description="Run the satellite bus UDP listener")
    parser.add_argument(
        "--key",
        default=None,
        help="HMAC secret; defaults to SATCOM_KEY env var or built-in demo value",
    )
    parser.add_argument(
        "--allowed-ground-stations",
        nargs="+",
        default=list(DEFAULT_ALLOWED),
        help="Space-separated list of allowed ground station identifiers",
    )
    parser.add_argument("--host", default=DEFAULT_ENDPOINT[0], help="Host interface to bind")
    parser.add_argument("--port", type=int, default=DEFAULT_ENDPOINT[1], help="UDP port to bind")
    return parser.parse_args()


def main() -> None:
    """Entry point for running the satellite bus listener."""
    args = parse_args()
    key, used_demo = resolve_hmac_key(args.key)
    if used_demo:
        logging.warning(
            "Using demo HMAC key; configure SATCOM_KEY or --key for stronger testing.",
        )
    bus = SatelliteBus(
        key=key,
        allowed_ground_ids=args.allowed_ground_stations,
        endpoint=(args.host, args.port),
    )
    bus.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
