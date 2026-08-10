"""What a probe is run against. `Target` is deliberately a narrow Protocol —
anything that can turn a conversation into a response text can be probed,
whether that's a raw LLM endpoint (the one adapter shipped here) or, later,
something that actually drives an agentic framework.

`Turn.role == "tool"` is what makes the prompt-injection category test
something specific to *agentic* systems rather than to LLMs generally: the
attacker-controlled content arrives as a tool result the model is asked to
act on, not as something the user typed.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from typing import Literal, Protocol, TypedDict
from urllib.request import Request, urlopen


class Turn(TypedDict):
    role: Literal["user", "assistant", "tool"]
    content: str


class Target(Protocol):
    def send(self, turns: Sequence[Turn]) -> str: ...


#: (url, payload, headers) -> parsed JSON response body. Defaults to a real
#: HTTP POST; tests inject a fake so no test ever touches the network.
PostFn = Callable[[str, dict[str, object], dict[str, str]], dict[str, object]]


def _real_post(url: str, payload: dict[str, object], headers: dict[str, str]) -> dict[str, object]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=headers, method="POST")
    with urlopen(request) as response:
        parsed = json.loads(response.read().decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{url}: expected a JSON object response, got {type(parsed).__name__}")  # noqa: TRY004
    return parsed


class HttpEndpointTarget:
    """Calls an OpenAI-compatible `chat/completions` endpoint — the shape
    most hosted and self-hosted gateways already speak, so this one adapter
    covers the common case without a framework-specific dependency."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str | None = None,
        post_fn: PostFn = _real_post,
    ) -> None:
        self._url = f"{base_url.rstrip('/')}/chat/completions"
        self._api_key = api_key
        self._model = model
        self._post_fn = post_fn

    def send(self, turns: Sequence[Turn]) -> str:
        payload: dict[str, object] = {
            "model": self._model,
            "messages": [{"role": t["role"], "content": t["content"]} for t in turns],
        }
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        response = self._post_fn(self._url, payload, headers)
        return _extract_message_content(response)


def _extract_message_content(response: dict[str, object]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError(f"response has no 'choices': {response!r}")
    first = choices[0]
    if not isinstance(first, dict):
        raise ValueError(f"response 'choices[0]' must be an object, got {first!r}")  # noqa: TRY004
    message = first.get("message")
    if not isinstance(message, dict):
        raise ValueError(f"response 'choices[0].message' missing or not an object: {first!r}")  # noqa: TRY004
    content = message.get("content")
    if not isinstance(content, str):
        raise ValueError(  # noqa: TRY004
            f"response 'choices[0].message.content' missing or not a string: {message!r}"
        )
    return content
