"""Subprocess wrapper for external tool invocations."""

import shutil
import subprocess
from collections.abc import Sequence

from video_qa.exceptions import ExternalToolError


def run_command(
    cmd: Sequence[str],
    timeout: int = 120,
    capture_stderr: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run an external command and return the result.

    Raises ExternalToolError on non-zero exit code.
    """
    try:
        result = subprocess.run(
            list(cmd),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise ExternalToolError(
            tool=str(cmd[0]),
            message=f"timed out after {timeout}s",
        ) from e
    except FileNotFoundError as e:
        raise ExternalToolError(
            tool=str(cmd[0]),
            message="command not found",
        ) from e

    if result.returncode != 0:
        stderr = result.stderr.strip() if capture_stderr else ""
        raise ExternalToolError(
            tool=str(cmd[0]),
            message=stderr or f"exit code {result.returncode}",
            returncode=result.returncode,
        )

    return result


def _find_magick_compare() -> list[str]:
    """Detect ImageMagick compare command (v6 vs v7)."""
    if shutil.which("magick"):
        return ["magick", "compare"]
    if shutil.which("compare"):
        return ["compare"]
    raise ExternalToolError(
        tool="ImageMagick",
        message="neither 'magick' nor 'compare' found in PATH. Install ImageMagick.",
    )


def check_dependencies() -> dict[str, str]:
    """Check that required external tools are available.

    Returns a dict of tool -> version string.
    Raises ExternalToolError if a required tool is missing.
    """
    tools: dict[str, str] = {}

    # ffmpeg / ffprobe
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise ExternalToolError(
                tool=tool,
                message=f"'{tool}' not found in PATH. Install ffmpeg.",
            )
        result = run_command([tool, "-version"], timeout=10)
        first_line = result.stdout.split("\n")[0]
        tools[tool] = first_line

    # ImageMagick
    compare_cmd = _find_magick_compare()
    tools["imagemagick_compare"] = " ".join(compare_cmd)

    return tools
