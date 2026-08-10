from pathlib import Path

import pytest
import yaml

from appeal_path_audit.channels import (
    EmailChannelConfig,
    EmailFormChannel,
    HttpChannelConfig,
    HttpFormChannel,
    ImapConfig,
    SmtpConfig,
    build_channel,
    load_channel_config,
)


def test_submit_posts_payload_and_returns_response():
    captured: dict[str, object] = {}

    def fake_post(
        url: str, method: str, payload: dict[str, object], headers: dict[str, str]
    ) -> tuple[int, str]:
        captured["url"] = url
        captured["method"] = method
        captured["payload"] = payload
        captured["headers"] = headers
        return 202, '{"ticket_id": "T-1"}'

    channel = HttpFormChannel(
        url="https://example.test/api/appeals",
        payload={"applicant_id": "TEST-0001", "reason": "requesting human review"},
        post_fn=fake_post,
    )

    result = channel.submit()

    assert result.status_code == 202
    assert result.body == '{"ticket_id": "T-1"}'
    assert captured["url"] == "https://example.test/api/appeals"
    assert captured["method"] == "POST"
    assert captured["payload"] == {"applicant_id": "TEST-0001", "reason": "requesting human review"}


def test_submit_uses_default_json_content_type_header():
    def fake_post(
        url: str, method: str, payload: dict[str, object], headers: dict[str, str]
    ) -> tuple[int, str]:
        assert headers["Content-Type"] == "application/json"
        return 200, "ok"

    channel = HttpFormChannel(url="https://example.test", payload={}, post_fn=fake_post)

    channel.submit()


def test_submit_respects_custom_method_and_headers():
    captured: dict[str, object] = {}

    def fake_post(
        url: str, method: str, payload: dict[str, object], headers: dict[str, str]
    ) -> tuple[int, str]:
        captured["method"] = method
        captured["headers"] = headers
        return 200, "ok"

    channel = HttpFormChannel(
        url="https://example.test",
        payload={},
        method="PUT",
        headers={"X-Api-Key": "test"},
        post_fn=fake_post,
    )

    channel.submit()

    assert captured["method"] == "PUT"
    assert captured["headers"] == {"X-Api-Key": "test"}


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data))


def test_load_channel_config_happy_path(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    _write_yaml(
        path,
        {
            "id": "loan-appeal",
            "url": "https://example.test/api/appeals",
            "payload": {"applicant_id": "TEST-0001"},
            "confirmation_marker": "ticket_id",
        },
    )

    config = load_channel_config(path)

    assert config.id == "loan-appeal"
    assert config.method == "POST"
    assert config.expected_status_min == 200
    assert config.expected_status_max == 299
    assert config.confirmation_marker == "ticket_id"


def test_load_channel_config_accepts_empty_payload(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    _write_yaml(path, {"id": "loan-appeal", "url": "https://example.test", "payload": {}})

    config = load_channel_config(path)

    assert config.payload == {}


def test_load_channel_config_raises_on_missing_field(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    _write_yaml(path, {"id": "loan-appeal", "url": "https://example.test"})

    with pytest.raises(ValueError, match="payload"):
        load_channel_config(path)


def test_load_channel_config_raises_on_non_mapping_payload(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    _write_yaml(
        path, {"id": "loan-appeal", "url": "https://example.test", "payload": "not a mapping"}
    )

    with pytest.raises(ValueError, match="'payload' must be a mapping"):
        load_channel_config(path)


def test_load_channel_config_raises_on_non_mapping_headers(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    _write_yaml(
        path,
        {
            "id": "loan-appeal",
            "url": "https://example.test",
            "payload": {"applicant_id": "TEST-0001"},
            "headers": "not a mapping",
        },
    )

    with pytest.raises(ValueError, match="'headers' must be a mapping"):
        load_channel_config(path)


def test_load_channel_config_raises_on_non_mapping_file(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    path.write_text("- just\n- a\n- list\n")

    with pytest.raises(ValueError, match="expected a YAML mapping"):
        load_channel_config(path)


def test_load_channel_config_defaults_to_http_channel_type(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    _write_yaml(path, {"id": "loan-appeal", "url": "https://example.test", "payload": {"a": 1}})

    config = load_channel_config(path)

    assert isinstance(config, HttpChannelConfig)


def test_load_channel_config_raises_on_unknown_channel_type(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    _write_yaml(path, {"channel_type": "carrier-pigeon", "id": "loan-appeal"})

    with pytest.raises(ValueError, match="unknown channel_type"):
        load_channel_config(path)


_EMAIL_CONFIG_DATA = {
    "channel_type": "email",
    "id": "loan-appeal-email",
    "to_addr": "appeals@example.test",
    "subject": "Requesting human review",
    "body": "Please review my case, applicant TEST-0001.",
    "smtp": {
        "host": "smtp.example.test",
        "port": 587,
        "username": "prober@example.test",
        "password_env": "SMTP_PASSWORD",
    },
    "imap": {
        "host": "imap.example.test",
        "port": 993,
        "username": "prober@example.test",
        "password_env": "IMAP_PASSWORD",
    },
}


def test_load_channel_config_email_happy_path(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    _write_yaml(path, _EMAIL_CONFIG_DATA)

    config = load_channel_config(path)

    assert isinstance(config, EmailChannelConfig)
    assert config.id == "loan-appeal-email"
    assert config.smtp.password_env == "SMTP_PASSWORD"
    assert config.imap.mailbox == "INBOX"
    assert config.expected_status_min == 200
    assert config.expected_status_max == 200


def test_load_channel_config_email_raises_on_missing_smtp_field(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    data = {**_EMAIL_CONFIG_DATA, "smtp": {"host": "smtp.example.test"}}
    _write_yaml(path, data)

    with pytest.raises(ValueError, match="'smtp' missing required field"):
        load_channel_config(path)


def test_load_channel_config_email_raises_on_missing_imap_field(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    data = {**_EMAIL_CONFIG_DATA, "imap": {"host": "imap.example.test"}}
    _write_yaml(path, data)

    with pytest.raises(ValueError, match="'imap' missing required field"):
        load_channel_config(path)


def test_load_channel_config_email_raises_on_non_mapping_smtp(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    data = {**_EMAIL_CONFIG_DATA, "smtp": "not a mapping"}
    _write_yaml(path, data)

    with pytest.raises(ValueError, match="'smtp' must be a mapping"):
        load_channel_config(path)


def test_load_channel_config_email_raises_on_missing_field(tmp_path: Path):
    path = tmp_path / "channel.yaml"
    data = {k: v for k, v in _EMAIL_CONFIG_DATA.items() if k != "to_addr"}
    _write_yaml(path, data)

    with pytest.raises(ValueError, match="to_addr"):
        load_channel_config(path)


def _smtp_config(**overrides: object) -> SmtpConfig:
    defaults: dict[str, object] = {
        "host": "smtp.example.test",
        "port": 587,
        "username": "prober@example.test",
        "password_env": "SMTP_PASSWORD",
    }
    return SmtpConfig(**{**defaults, **overrides})  # type: ignore[arg-type]


def _imap_config(**overrides: object) -> ImapConfig:
    defaults: dict[str, object] = {
        "host": "imap.example.test",
        "port": 993,
        "username": "prober@example.test",
        "password_env": "IMAP_PASSWORD",
    }
    return ImapConfig(**{**defaults, **overrides})  # type: ignore[arg-type]


def test_email_channel_submit_returns_reply_when_poll_finds_one():
    sent: dict[str, object] = {}

    def fake_send(to_addr, from_addr, subject, body, config):  # type: ignore[no-untyped-def]
        sent["to_addr"] = to_addr
        sent["from_addr"] = from_addr
        sent["subject"] = subject
        sent["body"] = body

    def fake_poll(marker, config, timeout_s, interval_s):  # type: ignore[no-untyped-def]
        sent["polled_marker"] = marker
        return "Thanks, ticket T-1 opened."

    channel = EmailFormChannel(
        to_addr="appeals@example.test",
        subject="Requesting human review",
        body="applicant TEST-0001",
        smtp_config=_smtp_config(),
        imap_config=_imap_config(),
        send_fn=fake_send,
        poll_fn=fake_poll,
    )

    result = channel.submit()

    assert result.status_code == 200
    assert result.body == "Thanks, ticket T-1 opened."
    assert sent["to_addr"] == "appeals@example.test"
    assert sent["from_addr"] == "prober@example.test"
    assert str(sent["subject"]).startswith("Requesting human review [appeal-probe-")
    # The same marker stitched into the subject is what the poll looks for.
    assert str(sent["polled_marker"]) in str(sent["subject"])


def test_email_channel_submit_returns_zero_status_when_no_reply_arrives():
    def fake_send(to_addr, from_addr, subject, body, config):  # type: ignore[no-untyped-def]
        pass

    def fake_poll(marker, config, timeout_s, interval_s):  # type: ignore[no-untyped-def]
        return None

    channel = EmailFormChannel(
        to_addr="appeals@example.test",
        subject="Requesting human review",
        body="applicant TEST-0001",
        smtp_config=_smtp_config(),
        imap_config=_imap_config(),
        send_fn=fake_send,
        poll_fn=fake_poll,
    )

    result = channel.submit()

    assert result.status_code == 0
    assert result.body == ""


def test_email_channel_defaults_from_addr_to_smtp_username():
    captured: dict[str, object] = {}

    def fake_send(to_addr, from_addr, subject, body, config):  # type: ignore[no-untyped-def]
        captured["from_addr"] = from_addr

    channel = EmailFormChannel(
        to_addr="appeals@example.test",
        subject="Requesting human review",
        body="applicant TEST-0001",
        smtp_config=_smtp_config(username="probe-account@example.test"),
        imap_config=_imap_config(),
        send_fn=fake_send,
        poll_fn=lambda *args: None,  # type: ignore[misc]
    )

    channel.submit()

    assert captured["from_addr"] == "probe-account@example.test"


def test_build_channel_returns_http_form_channel_for_http_config():
    config = HttpChannelConfig(id="loan-appeal", url="https://example.test", payload={})

    channel = build_channel(config)

    assert isinstance(channel, HttpFormChannel)


def test_build_channel_returns_email_form_channel_for_email_config():
    config = EmailChannelConfig(
        id="loan-appeal-email",
        to_addr="appeals@example.test",
        subject="Requesting human review",
        body="applicant TEST-0001",
        smtp=_smtp_config(),
        imap=_imap_config(),
    )

    channel = build_channel(config)

    assert isinstance(channel, EmailFormChannel)
