# Architecture Overview

The simulator models a simplified CCSDS command chain with authenticated uplink and defensive telemetry.

## Components
- **ground/** – Legitimate command generation using `CCSDSPacketBuilder` and `HMACSigner`.
- **satellite/** – UDP listener hardened by `SatelliteFirewall` and telemetry logging.
- **crypto/** – Reusable HMAC primitives.
- **ccsds/** – Packet structure definitions (primary/secondary headers and payload) and parsing helpers.
- **attacker/** – Rogue transmitter tooling for spoofing, malformed injections, and replay demonstrations.
- **cli/** – Convenience wrapper for launching the bus, sending commands, or executing attacks.
- **utils/** – Shared helpers such as HMAC key resolution.

## Data flow
1. **Command creation** – Ground station builds a CCSDS packet with a primary header, secondary header (timestamp + ground ID), payload (command string), and an HMAC-SHA256 signature across the unsigned portion.
2. **Transport** – Packets traverse a UDP socket emulating the RF uplink.
3. **Firewalling** – Satellite bus receives packets on UDP. `SatelliteFirewall` parses, checks allow-listed ground IDs, and validates the HMAC signature.
4. **Decisioning** – Accepted commands emit an "Executing command" telemetry entry; rejected or malformed packets emit warnings or critical security alerts.
5. **Attack simulation** – Rogue transmitter sends packets without the valid secret, demonstrating signature failures, malformed packet handling, and replay attempts.

## Security controls
- **Signature verification** – HMAC-SHA256 over unsigned headers + payload; verified using constant-time comparison.
- **Ground-station allow list** – Explicit set of authorized IDs blocks spoofed identifiers even when packets parse correctly.
- **Structured telemetry** – JSON-formatted events persisted to `telemetry.log` and stdout for easy ingestion by log processors.
- **Key management helper** – `utils.secrets.resolve_hmac_key` centralizes secret resolution from CLI args or environment variables and flags demo fallbacks.

## Operational notes
- Run the satellite bus first to bind the UDP port and start telemetry logging.
- Provide a strong `SATCOM_KEY` or `--key` to avoid demo-mode warnings.
- UDP sockets are intentionally simple and synchronous to keep the control flow clear; extend with asyncio or socket timeouts for higher fidelity.
