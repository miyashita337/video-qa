"""Frame comparison using ImageMagick RMSE."""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from video_qa._subprocess import _find_magick_compare
from video_qa.exceptions import ExternalToolError


@dataclass
class FrameDiff:
    """Result of comparing two adjacent frames."""

    frame_a: Path
    frame_b: Path
    rmse: float
    index: int


def _parse_rmse(stderr: str) -> float:
    """Parse RMSE value from ImageMagick compare output.

    ImageMagick outputs RMSE in various formats:
    - "123.456 (0.00189)" — normalized value in parens
    - "0.00189" — just the normalized value
    """
    # Try to find normalized value in parentheses first
    paren_match = re.search(r"\(([0-9.]+)\)", stderr)
    if paren_match:
        return float(paren_match.group(1))

    # Fall back to parsing a bare float
    float_match = re.search(r"([0-9]+\.?[0-9]*)", stderr)
    if float_match:
        value = float(float_match.group(1))
        # If > 1, it's the absolute value, not normalized — skip
        if value <= 1.0:
            return value

    return 0.0


def compare_frames(frames: list[Path]) -> list[FrameDiff]:
    """Compare adjacent frames and return RMSE diffs.

    Uses ImageMagick compare -metric RMSE.
    """
    if len(frames) < 2:
        return []

    compare_cmd = _find_magick_compare()
    diffs: list[FrameDiff] = []

    for i in range(len(frames) - 1):
        cmd = [
            *compare_cmd,
            "-metric",
            "RMSE",
            str(frames[i]),
            str(frames[i + 1]),
            "null:",
        ]

        # ImageMagick compare writes metrics to stderr.
        # Exit code 0 = identical, 1 = images differ (normal), 2 = error.
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except FileNotFoundError as e:
            raise ExternalToolError(
                tool="ImageMagick", message="compare command not found"
            ) from e

        if proc.returncode == 2:
            raise ExternalToolError(
                tool="ImageMagick",
                message=proc.stderr.strip(),
                returncode=2,
            )

        rmse = _parse_rmse(proc.stderr)

        diffs.append(
            FrameDiff(
                frame_a=frames[i],
                frame_b=frames[i + 1],
                rmse=rmse,
                index=i,
            )
        )

    return diffs
