"""Unified command-line interface for the uplink simulator."""

from __future__ import annotations

import argparse
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    """Return parsed arguments for orchestrating simulator components."""
    parser = argparse.ArgumentParser(description="Satellite uplink simulator CLI")
    sub = parser.add_subparsers(dest="component", required=True)

    bus = sub.add_parser("bus", help="Launch the satellite bus listener")
    bus.add_argument("--host", default="127.0.0.1", help="Host to bind")
    bus.add_argument("--port", type=int, default=5000, help="Port to bind")
    bus.add_argument("--key", default=None, help="HMAC key override")
    bus.add_argument(
        "--allowed-ground-stations",
        nargs="+",
        default=["GS-ALPHA"],
        help="Allowed ground station IDs",
    )

    gs = sub.add_parser("send", help="Send a legitimate command")
    gs.add_argument("command", help="Command string to send")
    gs.add_argument("--ground-id", default="GS-ALPHA")
    gs.add_argument("--key", default=None)
    gs.add_argument("--host", default="127.0.0.1")
    gs.add_argument("--port", type=int, default=5000)

    rogue = sub.add_parser("attack", help="Run a rogue transmission")
    rogue.add_argument("mode", choices=["spoof", "malformed"], help="Attack type")
    rogue.add_argument("--command", default="CMD: SHUTDOWN_THRUSTERS")
    rogue.add_argument("--ground-id", default="GS-ALPHA")
    rogue.add_argument("--host", default="127.0.0.1")
    rogue.add_argument("--port", type=int, default=5000)

    return parser.parse_args()


def main() -> None:
    """Entrypoint for the combined satellite simulator CLI."""
    args = parse_args()
    if args.component == "bus":
        cmd = [
            sys.executable,
            "-m",
            "satellite.satellite_bus",
            "--host",
            args.host,
            "--port",
            str(args.port),
            "--allowed-ground-stations",
            *args.allowed_ground_stations,
        ]
        if args.key:
            cmd.extend(["--key", args.key])
        subprocess.run(cmd, check=True)  # noqa: S603
    elif args.component == "send":
        cmd = [
            sys.executable,
            "-m",
            "ground.ground_station",
            args.command,
            "--ground-id",
            args.ground_id,
            "--host",
            args.host,
            "--port",
            str(args.port),
        ]
        if args.key:
            cmd.extend(["--key", args.key])
        subprocess.run(cmd, check=True)  # noqa: S603
    elif args.component == "attack":
        cmd = [
            sys.executable,
            "-m",
            "attacker.rogue_transmitter",
            "--host",
            args.host,
            "--port",
            str(args.port),
            args.mode,
        ]
        if args.mode == "spoof":
            cmd.extend([args.command, "--ground-id", args.ground_id])
        subprocess.run(cmd, check=True)  # noqa: S603


if __name__ == "__main__":
    main()
