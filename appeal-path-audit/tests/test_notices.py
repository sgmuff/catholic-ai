from pathlib import Path

import pytest

from appeal_path_audit.notices import load_notices


def test_load_notices_happy_path(tmp_path: Path):
    (tmp_path / "loan-denial.txt").write_text("Your application was denied by our system.")
    (tmp_path / "hiring-rejection.txt").write_text("We have decided not to move forward.")

    notices = load_notices(tmp_path)

    assert set(notices) == {"loan-denial", "hiring-rejection"}
    assert notices["loan-denial"].text == "Your application was denied by our system."


def test_load_notices_ignores_non_txt_files(tmp_path: Path):
    (tmp_path / "loan-denial.txt").write_text("denied")
    (tmp_path / "notes.md").write_text("not a notice")

    notices = load_notices(tmp_path)

    assert set(notices) == {"loan-denial"}


def test_load_notices_raises_on_empty_directory(tmp_path: Path):
    with pytest.raises(ValueError, match="no \\*.txt notice files found"):
        load_notices(tmp_path)
