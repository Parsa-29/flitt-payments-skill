#!/usr/bin/env python3
"""Generate or verify Flitt API signatures."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


EXCLUDED_KEYS = {"signature", "response_signature_string"}


def load_params(raw: str | None, params_file: str | None) -> dict[str, Any]:
    if bool(raw) == bool(params_file):
        raise SystemExit("Provide exactly one of --params or --params-file.")

    if params_file:
        data = json.loads(Path(params_file).read_text(encoding="utf-8"))
    else:
        data = json.loads(raw or "{}")

    if not isinstance(data, dict):
        raise SystemExit("Parameters must be a JSON object.")

    for root_key in ("request", "response"):
        inner = data.get(root_key)
        if isinstance(inner, dict):
            return inner

    return data


def is_present(value: Any) -> bool:
    return value is not None and value != ""


def stringify(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def signature_string(secret: str, params: dict[str, Any]) -> str:
    values = [
        stringify(params[key])
        for key in sorted(params)
        if key not in EXCLUDED_KEYS and is_present(params[key])
    ]
    return "|".join([secret, *values])


def generate_signature(secret: str, params: dict[str, Any]) -> str:
    payload = signature_string(secret, params).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or verify Flitt SHA1 signatures.")
    parser.add_argument("--secret", required=True, help="Flitt payment secret key.")
    parser.add_argument("--params", help="JSON object with request/response parameters.")
    parser.add_argument("--params-file", help="Path to JSON file with request/response parameters.")
    parser.add_argument("--verify", help="Expected signature to compare against.")
    parser.add_argument(
        "--no-string",
        action="store_true",
        help="Do not print the pre-hash signature string.",
    )
    args = parser.parse_args()

    params = load_params(args.params, args.params_file)
    pre_hash = signature_string(args.secret, params)
    digest = generate_signature(args.secret, params)

    if not args.no_string:
        print(f"string={pre_hash}")
    print(f"signature={digest}")

    if args.verify:
        expected = args.verify.lower()
        if digest == expected:
            print("verified=true")
            return 0
        print("verified=false", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
