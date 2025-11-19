# Operations and Runbook

This document captures operational guidance for running, observing, and troubleshooting the uplink simulator in lab or demo environments.

## Prerequisites
- Python 3.12+
- Dependencies installed via `pip install -r requirements.txt` or `make install`
- A strong HMAC secret provided via `SATCOM_KEY` or CLI `--key`.

## Standard workflows

### Start the satellite bus
```bash
python -m satellite.satellite_bus --host 0.0.0.0 --port 5000 --allowed-ground-stations GS-ALPHA GS-BETA --key "$SATCOM_KEY"
```

### Send a legitimate command
```bash
python -m ground.ground_station "CMD: ORIENT +10" --ground-id GS-ALPHA --host 127.0.0.1 --port 5000 --key "$SATCOM_KEY"
```

### Drive attacks and fuzzing
```bash
python -m attacker.rogue_transmitter spoof "CMD: RESET_COMPUTER" --ground-id GS-ALPHA
python -m attacker.rogue_transmitter malformed
python -m attacker.rogue_transmitter replay "<hex-packet>"
```

## Telemetry expectations
- Logs stream to stdout and `telemetry.log` in JSON lines format.
- Successful commands emit `"Command accepted"` followed by `"Executing command"` entries.
- Spoofed or malformed traffic emits `"CRITICAL SECURITY ALERT"` or `"Packet Decode Failure"` events with context (source IP, reason).

## Key management
- Prefer providing secrets via environment variables (e.g., `SATCOM_KEY`) or secure secret stores.
- The built-in demo key triggers a warning; rotate to a unique value for credible demos.
- Rotate keys by restarting the bus and ground station with the updated secret; replayed packets signed with the old key will fail verification.

## Troubleshooting tips
- **Socket bind errors**: ensure the port is free or adjust `--port`.
- **Repeated decode failures**: confirm the transmitter and bus agree on packet length and signature settings; inspect `telemetry.log` for parsing reasons.
- **HMAC failures for known-good traffic**: verify both sides use the same secret and ground station ID; delete stale captures used for replay.
- **Slow shutdown**: send `Ctrl+C`; the bus catches `KeyboardInterrupt` and emits a shutdown telemetry message.

## Maintenance tasks
- Run `make ci` before commits to ensure lint, type-check, and tests pass.
- Keep dependencies updated; CI targets Python 3.12.
- Use `.pre-commit-config.yaml` to install hooks that enforce formatting and static analysis locally.
