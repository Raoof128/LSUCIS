# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities privately by email to security@example.com. Do not open public issues for sensitive reports.

We aim to acknowledge reports within 2 business days and provide a remediation timeline after triage.

## Operational security

- Never commit real SATCOM or HMAC keys to the repository or logs.
- Use the `SATCOM_KEY` environment variable or `--key` CLI flag to provide secrets at runtime.
- Telemetry is JSON-formatted and may contain command payloads; handle log files accordingly.

## Supported Versions

Security fixes will be applied to the latest main branch. Older releases may receive fixes at the maintainers' discretion.
