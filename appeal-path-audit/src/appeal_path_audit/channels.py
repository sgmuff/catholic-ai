"""What a documented appeal channel actually is, and whether it works. This
only checks reachability — that a submission is accepted and acknowledged —
never whether a human genuinely reconsidered the case. That deeper question
isn't mechanically checkable, so `runner.py` always captures the response
for a person to read rather than scoring it.

Two channel shapes: `HttpFormChannel` for a documented appeal endpoint that
accepts a POST, and `EmailFormChannel` for one documented as an email
address instead. Both report through the same `ChannelResponse` shape so
`runner.probe_channel` doesn't need to know which kind it's looking at —
for email, `status_code` is a synthetic signal (200 = a reply arrived
within the poll window, 0 = it didn't), since email has no HTTP status of
its own.
"""

from __future__ import annotations

import email.policy
import imaplib
import json
import os
import smtplib
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Protocol
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
class SmtpConfig:
    host: str
    port: int
    username: str
    #: Name of the environment variable holding the password — never the
    #: password itself, so a committed channel.yaml can't leak a credential.
    password_env: str
    use_tls: bool = True


@dataclass(frozen=True)
class ImapConfig:
    host: str
    port: int
    username: str
    password_env: str
    mailbox: str = "INBOX"
    use_ssl: bool = True


def _resolve_password(env_var: str) -> str:
    value = os.environ.get(env_var)
    if not value:
        raise ValueError(f"environment variable {env_var!r} is not set")
    return value


#: (to_addr, from_addr, subject, body, config) -> None. Defaults to a real
#: SMTP send; tests inject a fake so no test ever touches the network.
SendFn = Callable[[str, str, str, str, SmtpConfig], None]

#: (subject_marker, config, timeout_s, interval_s) -> reply body, or None if
#: no matching reply arrived before the timeout. Defaults to real IMAP
#: polling; tests inject a fake so no test ever touches the network.
PollFn = Callable[[str, ImapConfig, float, float], str | None]


def _real_smtp_send(
    to_addr: str, from_addr: str, subject: str, body: str, config: SmtpConfig
) -> None:
    message = EmailMessage()
    message["To"] = to_addr
    message["From"] = from_addr
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(config.host, config.port) as smtp:
        if config.use_tls:
            smtp.starttls()
        smtp.login(config.username, _resolve_password(config.password_env))
        smtp.send_message(message)


def _extract_text_body(message: EmailMessage) -> str:
    body_part = message.get_body(preferencelist=("plain",))
    if body_part is None:
        return ""
    content = body_part.get_content()
    return content if isinstance(content, str) else str(content)


def _real_imap_poll(
    marker: str, config: ImapConfig, timeout_s: float, interval_s: float
) -> str | None:
    password = _resolve_password(config.password_env)
    imap_cls = imaplib.IMAP4_SSL if config.use_ssl else imaplib.IMAP4
    deadline = time.monotonic() + timeout_s
    while True:
        with imap_cls(config.host, config.port) as imap:
            imap.login(config.username, password)
            imap.select(config.mailbox)
            status, data = imap.search(None, "SUBJECT", marker)
            if status == "OK" and data and data[0]:
                msg_num = data[0].split()[-1]
                fetch_status, msg_data = imap.fetch(msg_num, "(RFC822)")
                if fetch_status == "OK" and msg_data and isinstance(msg_data[0], tuple):
                    raw = msg_data[0][1]
                    parsed = email.message_from_bytes(raw, policy=email.policy.default)
                    assert isinstance(parsed, EmailMessage)
                    return _extract_text_body(parsed)
        if time.monotonic() >= deadline:
            return None
        time.sleep(interval_s)


class EmailFormChannel:
    """Submits a synthetic appeal request by email, then polls a mailbox
    for a reply within a bounded window — covers appeal channels documented
    as an email address rather than a web form. A unique marker is stitched
    into the subject line so the poll can find the right reply (or its
    auto-ack) without relying on In-Reply-To/References threading, which an
    auto-responder isn't guaranteed to set. Reachability here still only
    means "a reply arrived" — see the module docstring."""

    def __init__(
        self,
        to_addr: str,
        subject: str,
        body: str,
        smtp_config: SmtpConfig,
        imap_config: ImapConfig,
        from_addr: str | None = None,
        poll_timeout_s: float = 300.0,
        poll_interval_s: float = 15.0,
        send_fn: SendFn = _real_smtp_send,
        poll_fn: PollFn = _real_imap_poll,
    ) -> None:
        self._to_addr = to_addr
        self._subject = subject
        self._body = body
        self._smtp_config = smtp_config
        self._imap_config = imap_config
        self._from_addr = from_addr or smtp_config.username
        self._poll_timeout_s = poll_timeout_s
        self._poll_interval_s = poll_interval_s
        self._send_fn = send_fn
        self._poll_fn = poll_fn

    def submit(self) -> ChannelResponse:
        marker = f"appeal-probe-{uuid.uuid4().hex[:12]}"
        tagged_subject = f"{self._subject} [{marker}]"
        self._send_fn(self._to_addr, self._from_addr, tagged_subject, self._body, self._smtp_config)
        reply_body = self._poll_fn(
            marker, self._imap_config, self._poll_timeout_s, self._poll_interval_s
        )
        if reply_body is None:
            return ChannelResponse(status_code=0, body="")
        return ChannelResponse(status_code=200, body=reply_body)


@dataclass(frozen=True)
class HttpChannelConfig:
    id: str
    url: str
    payload: dict[str, object]
    method: str = "POST"
    headers: dict[str, str] | None = None
    expected_status_min: int = 200
    expected_status_max: int = 299
    confirmation_marker: str | None = None


@dataclass(frozen=True)
class EmailChannelConfig:
    id: str
    to_addr: str
    subject: str
    body: str
    smtp: SmtpConfig
    imap: ImapConfig
    from_addr: str | None = None
    poll_timeout_s: float = 300.0
    poll_interval_s: float = 15.0
    expected_status_min: int = 200
    expected_status_max: int = 200
    confirmation_marker: str | None = None


ChannelConfig = HttpChannelConfig | EmailChannelConfig


_HTTP_REQUIRED_FIELDS = ("id", "url", "payload")
_EMAIL_REQUIRED_FIELDS = ("id", "to_addr", "subject", "body", "smtp", "imap")
_SMTP_REQUIRED_FIELDS = ("host", "port", "username", "password_env")
_IMAP_REQUIRED_FIELDS = ("host", "port", "username", "password_env")

#: fields where an empty value (e.g. `payload: {}`) is still a legitimate,
#: present value — only truly missing keys count as an error for these.
_ALLOWS_EMPTY_VALUE = frozenset({"payload"})


def _is_missing(data: dict[str, object], field: str) -> bool:
    if field in _ALLOWS_EMPTY_VALUE:
        return field not in data
    return not data.get(field)


def _require_mapping(data: dict[str, Any], field: str, path: Path) -> dict[str, Any]:
    value = data.get(field)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: {field!r} must be a mapping")  # noqa: TRY004
    return value


def _load_http_channel_config(data: dict[str, Any], path: Path) -> HttpChannelConfig:
    missing = [f for f in _HTTP_REQUIRED_FIELDS if _is_missing(data, f)]
    if missing:
        raise ValueError(f"{path}: channel config missing required field(s) {missing}")
    payload = data["payload"]
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: 'payload' must be a mapping")  # noqa: TRY004
    headers = data.get("headers")
    if headers is not None and not isinstance(headers, dict):
        raise ValueError(f"{path}: 'headers' must be a mapping if given")
    return HttpChannelConfig(
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


def _load_smtp_config(data: dict[str, Any], path: Path) -> SmtpConfig:
    missing = [f for f in _SMTP_REQUIRED_FIELDS if not data.get(f)]
    if missing:
        raise ValueError(f"{path}: 'smtp' missing required field(s) {missing}")
    return SmtpConfig(
        host=str(data["host"]),
        port=int(data["port"]),
        username=str(data["username"]),
        password_env=str(data["password_env"]),
        use_tls=bool(data.get("use_tls", True)),
    )


def _load_imap_config(data: dict[str, Any], path: Path) -> ImapConfig:
    missing = [f for f in _IMAP_REQUIRED_FIELDS if not data.get(f)]
    if missing:
        raise ValueError(f"{path}: 'imap' missing required field(s) {missing}")
    return ImapConfig(
        host=str(data["host"]),
        port=int(data["port"]),
        username=str(data["username"]),
        password_env=str(data["password_env"]),
        mailbox=str(data.get("mailbox", "INBOX")),
        use_ssl=bool(data.get("use_ssl", True)),
    )


def _load_email_channel_config(data: dict[str, Any], path: Path) -> EmailChannelConfig:
    missing = [f for f in _EMAIL_REQUIRED_FIELDS if _is_missing(data, f)]
    if missing:
        raise ValueError(f"{path}: channel config missing required field(s) {missing}")
    smtp = _load_smtp_config(_require_mapping(data, "smtp", path), path)
    imap = _load_imap_config(_require_mapping(data, "imap", path), path)
    return EmailChannelConfig(
        id=str(data["id"]),
        to_addr=str(data["to_addr"]),
        subject=str(data["subject"]),
        body=str(data["body"]),
        smtp=smtp,
        imap=imap,
        from_addr=str(data["from_addr"]) if data.get("from_addr") else None,
        poll_timeout_s=float(data.get("poll_timeout_s", 300.0)),
        poll_interval_s=float(data.get("poll_interval_s", 15.0)),
        expected_status_min=int(data.get("expected_status_min", 200)),
        expected_status_max=int(data.get("expected_status_max", 200)),
        confirmation_marker=str(data["confirmation_marker"])
        if data.get("confirmation_marker")
        else None,
    )


def load_channel_config(path: Path) -> ChannelConfig:
    """Loads one channel-probe configuration — a documented appeal
    endpoint and the synthetic test request to submit to it. `channel_type`
    (`http`, the default, or `email`) picks which shape the rest of the
    file must have. Raises ValueError, naming what's wrong, on anything
    malformed."""
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping, got {type(data).__name__}")  # noqa: TRY004
    channel_type = str(data.get("channel_type", "http"))
    if channel_type == "http":
        return _load_http_channel_config(data, path)
    if channel_type == "email":
        return _load_email_channel_config(data, path)
    raise ValueError(f"{path}: unknown channel_type {channel_type!r}; must be 'http' or 'email'")


def build_channel(config: ChannelConfig) -> Channel:
    """The default `ChannelFactory` used by `runner.main` — builds the
    channel implementation matching whatever `load_channel_config` loaded."""
    if isinstance(config, HttpChannelConfig):
        return HttpFormChannel(
            url=config.url, payload=config.payload, method=config.method, headers=config.headers
        )
    return EmailFormChannel(
        to_addr=config.to_addr,
        subject=config.subject,
        body=config.body,
        smtp_config=config.smtp,
        imap_config=config.imap,
        from_addr=config.from_addr,
        poll_timeout_s=config.poll_timeout_s,
        poll_interval_s=config.poll_interval_s,
    )
