#!/usr/bin/env python3
"""Minimal, dependency-free webhook forwarder for Cognis findings.

Reads JSON findings on stdin and POSTs them to a URL (SIEM/Slack/Jira bridge).
Usage:  <tool> scan . --format json | python integrations/webhook.py --url URL
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

_ALLOWED_SCHEMES = {"http", "https"}


def _validate_url(url: str) -> str:
    """Return *url* unchanged; raise ValueError with a clear message if invalid."""
    try:
        parsed = urlparse(url)
    except Exception as exc:
        raise ValueError(f"Cannot parse URL: {exc}") from exc
    if not parsed.scheme:
        raise ValueError(f"URL is missing a scheme (expected http or https): {url!r}")
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError(
            f"Unsupported URL scheme {parsed.scheme!r}. "
            f"Allowed: {', '.join(sorted(_ALLOWED_SCHEMES))}"
        )
    if not parsed.netloc:
        raise ValueError(f"URL is missing a host: {url!r}")
    return url


def _parse_header(raw: str) -> tuple[str, str]:
    """Parse a 'Key: Value' header string.

    Raises ValueError if the colon separator is absent or the key is empty.
    """
    if ":" not in raw:
        raise ValueError(
            f"Header {raw!r} is missing a colon separator. "
            "Expected format: 'Key: Value'"
        )
    k, _, v = raw.partition(":")
    k = k.strip()
    if not k:
        raise ValueError(f"Header key is empty in {raw!r}")
    return k, v.strip()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="POST JSON findings from stdin to a webhook URL."
    )
    ap.add_argument("--url", required=True, help="Destination URL (http/https)")
    ap.add_argument(
        "--header",
        action="append",
        default=[],
        metavar="Key: Value",
        help="Extra request header; may be repeated",
    )
    args = ap.parse_args()

    # --- validate URL --------------------------------------------------------
    try:
        url = _validate_url(args.url)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # --- validate headers ----------------------------------------------------
    parsed_headers: list[tuple[str, str]] = []
    for raw in args.header:
        try:
            parsed_headers.append(_parse_header(raw))
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    # --- read and validate stdin ---------------------------------------------
    raw_stdin = sys.stdin.read()
    if not raw_stdin.strip():
        print("error: no input on stdin -- nothing to send", file=sys.stderr)
        return 2

    try:
        json.loads(raw_stdin)
    except json.JSONDecodeError as exc:
        print(f"error: stdin is not valid JSON: {exc}", file=sys.stderr)
        return 2

    payload = raw_stdin.encode("utf-8")

    # --- send ----------------------------------------------------------------
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in parsed_headers:
        req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"posted {len(payload)} bytes -> {r.status}")
        return 0
    except urllib.error.HTTPError as exc:
        print(f"webhook error: HTTP {exc.code} {exc.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"webhook error: {exc.reason}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"webhook error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
