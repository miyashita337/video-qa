"""E2E tests for the CLI pipeline."""

import shutil

import pytest
from typer.testing import CliRunner

from video_qa.cli import app

runner = CliRunner()

requires_ffmpeg = pytest.mark.skipif(
    not shutil.which("ffmpeg"),
    reason="ffmpeg not installed",
)
requires_imagemagick = pytest.mark.skipif(
    not shutil.which("magick") and not shutil.which("compare"),
    reason="ImageMagick not installed",
)


@requires_ffmpeg
@requires_imagemagick
def test_analyze_test_video(tmp_path: str) -> None:
    """E2E: generate a test video and run the full pipeline."""
    import subprocess
    from pathlib import Path

    tmp = Path(tmp_path)
    video = tmp / "test.mp4"

    # Generate red-blue-red test video (3 seconds)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=red:size=160x120:d=1,format=yuv420p",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:size=160x120:d=1,format=yuv420p",
            "-f",
            "lavfi",
            "-i",
            "color=c=red:size=160x120:d=1,format=yuv420p",
            "-filter_complex",
            "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]",
            "-map",
            "[v]",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(video),
        ],
        capture_output=True,
        check=True,
    )

    output_dir = tmp / "output"
    result = runner.invoke(
        app,
        [
            str(video),
            "--fps",
            "5",
            "--threshold",
            "0.05",
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert "regions detected" in result.output.lower()
    assert (output_dir / "report.md").exists()
    assert (output_dir / "images").is_dir()


def test_analyze_nonexistent_file() -> None:
    result = runner.invoke(app, ["/nonexistent/video.mp4"])
    assert result.exit_code == 1


def test_analyze_invalid_fps() -> None:
    result = runner.invoke(
        app,
        [
            "/tmp/any.mp4",
            "--fps",
            "0",
        ],
    )
    assert result.exit_code == 1
