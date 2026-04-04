"""Tests for subprocess wrapper."""

from unittest.mock import patch

import pytest

from video_qa._subprocess import (
    _find_magick_compare,
    check_dependencies,
    run_command,
)
from video_qa.exceptions import ExternalToolError


def test_run_command_success() -> None:
    result = run_command(["echo", "hello"])
    assert result.stdout.strip() == "hello"
    assert result.returncode == 0


def test_run_command_nonzero_exit() -> None:
    with pytest.raises(ExternalToolError, match="exit code"):
        run_command(["false"])


def test_run_command_not_found() -> None:
    with pytest.raises(ExternalToolError, match="command not found"):
        run_command(["nonexistent_command_xyz"])


def test_run_command_timeout() -> None:
    with pytest.raises(ExternalToolError, match="timed out"):
        run_command(["sleep", "10"], timeout=1)


def test_find_magick_compare_v7() -> None:
    with patch("shutil.which", side_effect=lambda x: x == "magick"):
        result = _find_magick_compare()
        assert result == ["magick", "compare"]


def test_find_magick_compare_v6() -> None:
    def which(cmd: str) -> str | None:
        if cmd == "compare":
            return "/usr/bin/compare"
        return None

    with patch("shutil.which", side_effect=which):
        result = _find_magick_compare()
        assert result == ["compare"]


def test_find_magick_compare_missing() -> None:
    with (
        patch("shutil.which", return_value=None),
        pytest.raises(ExternalToolError, match="ImageMagick"),
    ):
        _find_magick_compare()


def test_check_dependencies_missing_ffmpeg() -> None:
    def which(cmd: str) -> str | None:
        if cmd == "ffmpeg":
            return None
        return f"/usr/bin/{cmd}"

    with (
        patch("video_qa._subprocess.shutil.which", side_effect=which),
        pytest.raises(ExternalToolError, match="ffmpeg"),
    ):
        check_dependencies()
