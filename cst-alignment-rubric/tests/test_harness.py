import pytest

from eval.harness import run


def test_run_not_yet_implemented():
    """Placeholder: harness.run() is unbuilt scaffolding, not real behavior yet.

    Replace this with real coverage as soon as run() does something —
    an always-passing placeholder test earns nothing on its own.
    """
    with pytest.raises(NotImplementedError):
        run(scenario_dir="rubric/scenarios", target_config="")
