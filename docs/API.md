# API and Module Reference

This reference summarizes the key modules that make up the uplink security simulator.

## Crypto
- **`crypto.constants.HMAC_DIGEST_LENGTH`** – Shared constant representing the digest length for all HMAC operations (keeps builders and parsers aligned).
- **`crypto.hmac_signer.HMACSigner`** – Generates HMAC-SHA256 signatures for unsigned CCSDS packet bytes. Provides `sign` and `hexdigest` helpers.
- **`crypto.verifier.HMACVerifier`** – Validates HMAC-SHA256 signatures using constant-time comparison.

## CCSDS Helpers
- **`ccsds.packet_builder.CCSDSPacketBuilder`** – Builds CCSDS-style primary/secondary headers, encodes payloads, and appends HMAC signatures.
- **`ccsds.packet_parser.CCSDSPacketParser`** – Parses incoming packets, returning structured `ParsedPacket` objects or raising `PacketValidationError` on failure.

## Satellite Side
- **`satellite.firewall.SatelliteFirewall`** – Parses packets, enforces ground-station allow lists, validates HMACs, and emits structured telemetry. Returns `FirewallDecision` objects.
- **`satellite.satellite_bus.SatelliteBus`** – UDP listener that feeds packets into the firewall and emits execution events.
- **`satellite.telemetry.TelemetryLogger`** – Structured logger that writes JSON payloads to both stdout and `telemetry.log`.

## Ground Station
- **`ground.ground_station.GroundStation`** – Builds and dispatches authenticated CCSDS commands to the configured satellite endpoint.

## Attacker Toolkit
- **`attacker.rogue_transmitter.RogueTransmitter`** – Sends spoofed, malformed, or replayed packets to exercise defensive logic.

## Shared Utilities
- **`utils.secrets.resolve_hmac_key`** – Centralized helper for resolving the HMAC key from CLI arguments or environment variables while signalling when a demo fallback was used.

## Command-Line Interfaces
- **`python -m satellite.satellite_bus`** – Start the satellite UDP listener. Accepts `--allowed-ground-stations`, `--host`, `--port`, and `--key` arguments.
- **`python -m ground.ground_station <command>`** – Send a signed command. Supports `--ground-id`, `--host`, `--port`, and `--key` arguments.
- **`python -m attacker.rogue_transmitter <mode>`** – Execute spoofing or malformed packet injections. Supports `spoof`, `malformed`, and `replay` modes.
- **`python -m cli.satcli ...`** – Convenience wrapper to orchestrate the above tools.

## Error Handling
- All packet parsing errors raise `PacketValidationError` and emit telemetry with the failure reason.
- HMAC verification failures are logged as critical security alerts and rejected before execution.

## Telemetry Output Schema
Each telemetry line contains JSON with at least `timestamp` and `message` fields plus contextual metadata such as `source_ip`, `command`, `ground_station_id`, or `reason`.
