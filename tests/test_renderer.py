"""Tests for image rendering."""

from pathlib import Path

from PIL import Image

from video_qa.core.clusterer import Region
from video_qa.core.renderer import render_annotated_frame, render_timeline


def test_annotated_frame_created(
    sample_frames: list[Path],
    tmp_path: Path,
) -> None:
    output = tmp_path / "annotated.png"
    result = render_annotated_frame(
        sample_frames[0],
        "Test Label",
        output,
    )
    assert result.exists()
    img = Image.open(result)
    assert img.width == 64
    assert img.height == 48


def test_timeline_combines_three_frames(
    sample_frames: list[Path],
    tmp_path: Path,
) -> None:
    region = Region(
        start_index=1,
        end_index=3,
        peak_index=2,
        before_frame=sample_frames[0],
        peak_frame=sample_frames[2],
        after_frame=sample_frames[4],
        max_rmse=0.82,
        timestamp_start=0.2,
        timestamp_end=0.6,
    )
    output = tmp_path / "timeline.png"
    result = render_timeline(region, output, fps=5)
    assert result.exists()
    img = Image.open(result)
    # 3 images of 64px wide + 2 gaps of 4px = 200px
    assert img.width == 64 * 3 + 4 * 2
    # Height = image height + label height (40)
    assert img.height == 48 + 40
