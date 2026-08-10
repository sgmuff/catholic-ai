"""What a documented appeal channel actually is, and whether it works. This
only checks reachability — that a submission is accepted and acknowledged —
never whether a human genuinely reconsidered the case. That deeper question
isn't mechanically checkable, so `runner.py` always captures the response
for a person to read rather than scoring it.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.request import Request, urlopen

import yaml


@dataclass(frozen=True)
class ChannelResponse:
    status_code: int
    body: str


class Channel(Protocol):
    def submit(self) -> ChannelResponse: ...


#: (url, method, payload, headers) -> (status_code, body). Defaults to a
#: real HTTP call; tests inject a fake so no test ever touches the network.
PostFn = Callable[[str, str, dict[str, object], dict[str, str]], tuple[int, str]]


def _real_post(
    url: str, method: str, payload: dict[str, object], headers: dict[str, str]
) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=headers, method=method)
    with urlopen(request) as response:
        return response.status, response.read().decode("utf-8")


class HttpFormChannel:
    """Submits a configured payload to a documented appeal endpoint —
    covers the common case of a contact/appeal form that accepts a POST,
    without assuming any particular schema for the payload or response."""

    def __init__(
        self,
        url: str,
        payload: dict[str, object],
        method: str = "POST",
        headers: dict[str, str] | None = None,
        post_fn: PostFn = _real_post,
    ) -> None:
        self._url = url
        self._method = method
        self._payload = payload
        self._headers = headers or {"Content-Type": "application/json"}
        self._post_fn = post_fn

    def submit(self) -> ChannelResponse:
        status_code, body = self._post_fn(self._url, self._method, self._payload, self._headers)
        return ChannelResponse(status_code=status_code, body=body)


@dataclass(frozen=True)
class ChannelConfig:
    id: str
    url: str
    payload: dict[str, object]
    method: str = "POST"
    headers: dict[str, str] | None = None
    expected_status_min: int = 200
    expected_status_max: int = 299
    confirmation_marker: str | None = None


_REQUIRED_CONFIG_FIELDS = ("id", "url", "payload")

#: fields where an empty value (e.g. `payload: {}`) is still a legitimate,
#: present value — only truly missing keys count as an error for these.
_ALLOWS_EMPTY_VALUE = frozenset({"payload"})


def _is_missing(data: dict[str, object], field: str) -> bool:
    if field in _ALLOWS_EMPTY_VALUE:
        return field not in data
    return not data.get(field)


def load_channel_config(path: Path) -> ChannelConfig:
    """Loads one channel-probe configuration — a documented appeal
    endpoint and the synthetic test request to submit to it. Raises
    ValueError, naming what's wrong, on anything malformed."""
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping, got {type(data).__name__}")  # noqa: TRY004
    missing = [f for f in _REQUIRED_CONFIG_FIELDS if _is_missing(data, f)]
    if missing:
        raise ValueError(f"{path}: channel config missing required field(s) {missing}")
    payload = data["payload"]
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: 'payload' must be a mapping")  # noqa: TRY004
    headers = data.get("headers")
    if headers is not None and not isinstance(headers, dict):
        raise ValueError(f"{path}: 'headers' must be a mapping if given")
    return ChannelConfig(
        id=str(data["id"]),
        url=str(data["url"]),
        payload=payload,
        method=str(data.get("method", "POST")),
        headers=headers,
        expected_status_min=int(data.get("expected_status_min", 200)),
        expected_status_max=int(data.get("expected_status_max", 299)),
        confirmation_marker=str(data["confirmation_marker"])
        if data.get("confirmation_marker")
        else None,
    )
