# Contributing

Thank you for your interest in improving the LEO Satellite Uplink "Command Intrusion" Simulator. We welcome issues, ideas, and pull requests.

## Development workflow

1. Fork the repository and create a topic branch.
2. Create a virtual environment and install dependencies from `requirements.txt` (or use `make install`).
3. Run `make ci` (ruff, mypy, pytest) before submitting a pull request.
4. Ensure new code paths include logging, type hints, and docstrings.
5. Update documentation (README, architecture docs, operations runbook, examples) when behavior changes.
6. Install the provided pre-commit hooks with `pre-commit install` to keep formatting and typing consistent.

## Commit messages

Use clear, descriptive commit messages. Reference issues when appropriate.

## Code style

- Follow the existing module layouts and naming conventions.
- Keep functions small and focused; prefer pure functions where practical.
- Avoid catching broad exceptions. Handle expected errors explicitly.
- Use the logging utilities already provided instead of `print` for operational events.

## Reporting security concerns

If you find a potential vulnerability, please follow the guidance in `SECURITY.md` and avoid filing public issues until the problem is addressed.
