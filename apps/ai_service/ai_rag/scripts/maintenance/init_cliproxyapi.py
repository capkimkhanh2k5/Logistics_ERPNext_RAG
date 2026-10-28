"""Create private local CLIProxyAPI settings without replacing existing credentials."""

from __future__ import annotations

import argparse
import os
import secrets
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = PROJECT_ROOT / "config" / "cliproxyapi"


def initialize(directory: Path) -> bool:
    config_path = directory / "config.yaml"
    credentials_path = directory / "credentials.env"
    existing = [path.exists() for path in (config_path, credentials_path)]
    if all(existing):
        return False
    if any(existing):
        raise ValueError(
            f"Incomplete setup in {directory}; restore the missing file before continuing."
        )

    template = (CONFIG_ROOT / "config.example.yaml").read_text(encoding="utf-8")
    if template.count("__CLIENT_API_KEY__") != 1:
        raise ValueError("Expected exactly one client key placeholder in the config template.")

    client_key = "cpa-client-" + secrets.token_urlsafe(32)
    management_key = "cpa-admin-" + secrets.token_urlsafe(32)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    files = {
        config_path: template.replace("__CLIENT_API_KEY__", client_key),
        credentials_path: (
            "# Local secrets. Do not commit or share this file.\n"
            f"MANAGEMENT_PASSWORD={management_key}\n"
            f"CLIPROXYAPI_CLIENT_API_KEY={client_key}\n"
        ),
    }
    for path, content in files.items():
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=CONFIG_ROOT / "local")
    args = parser.parse_args()
    try:
        created = initialize(args.directory)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    print(f"{'Created' if created else 'Preserved existing'} local setup: {args.directory}")
    print("Management password and client API key are in credentials.env; values are not printed.")


if __name__ == "__main__":
    main()
