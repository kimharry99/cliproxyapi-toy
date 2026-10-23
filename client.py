"""Local proxy key -> one chat request -> assistant text, using only stdlib."""

from __future__ import annotations

import http.client
import json
import os
import sys
import urllib.parse

BASE_URL = "http://127.0.0.1:18317/v1/chat/completions"
PROXY_URL = urllib.parse.urlsplit(BASE_URL)
CLIENT_KEY = os.environ.get("CLIPROXY_CLIENT_KEY", "")

MODEL = "gpt-6-luna"
TIMEOUT_SECONDS = 180


def main() -> int:
    """Load the key and message, send once, then print the assistant reply."""
    # 1. Read the local proxy key; the proxy handles account authentication.
    client_key = os.environ.get("CLIPROXY_CLIENT_KEY", "")

    message = "Hello. Please reply in one sentence."
    request_body = build_request(message)

    # 2. Let the HTTP library send the header and report transport errors.
    status, raw_body = send_request(client_key, request_body)
    if not 200 <= status < 300:
        print(f"HTTP {status}: proxy request failed", file=sys.stderr)
        return 1

    # 3. Extract and print the assistant text.
    reply = extract_reply(raw_body)
    print(reply)
    return 0


def build_request(message: str) -> bytes:
    """Encode one nonstreaming request for the fixed model."""
    return json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": message}],
            "stream": False,
        }
    ).encode()


def send_request(client_key: str, request_body: bytes) -> tuple[int, str]:
    """POST once, close resources, and propagate HTTP-library exceptions."""
    headers = {
        "Authorization": "Bearer " + client_key,
        "Content-Type": "application/json",
    }
    connection = http.client.HTTPConnection(
        PROXY_URL.hostname, PROXY_URL.port, timeout=TIMEOUT_SECONDS
    )
    try:
        connection.request(
            "POST",
            PROXY_URL.path,
            body=request_body,
            headers=headers,
        )
        with connection.getresponse() as response:
            return (response.status, response.read().decode("utf-8", errors="replace"))
    finally:
        connection.close()


def extract_reply(raw_body: str) -> str:
    """Decode JSON."""
    response_body = json.loads(raw_body)
    reply = response_body["choices"][0]["message"]["content"]

    return reply


if __name__ == "__main__":
    sys.exit(main())
