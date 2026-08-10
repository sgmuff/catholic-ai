from pathlib import Path

import pytest
import yaml

from appeal_path_audit.channels import HttpFormChannel, load_channel_config


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
