"""Shared test fixtures for video-qa."""

from pathlib import Path

import pytest
from PIL import Image

from video_qa.core.comparator import FrameDiff


@pytest.fixture()
def sample_frames(tmp_path: Path) -> list[Path]:
    """Generate 5 test frames: red, red, blue, blue, red."""
    colors = [
        (255, 0, 0),
        (255, 0, 0),
        (0, 0, 255),
        (0, 0, 255),
        (255, 0, 0),
    ]
    paths: list[Path] = []
    for i, color in enumerate(colors):
        img = Image.new("RGB", (64, 48), color)
        p = tmp_path / f"frame_{i:06d}.png"
        img.save(p)
        paths.append(p)
    return paths


@pytest.fixture()
def sample_diffs(sample_frames: list[Path]) -> list[FrameDiff]:
    """Pre-computed diffs for sample_frames (red-red-blue-blue-red)."""
    return [
        FrameDiff(
            frame_a=sample_frames[0],
            frame_b=sample_frames[1],
            rmse=0.0,
            index=0,
        ),
        FrameDiff(
            frame_a=sample_frames[1],
            frame_b=sample_frames[2],
            rmse=0.82,
            index=1,
        ),
        FrameDiff(
            frame_a=sample_frames[2],
            frame_b=sample_frames[3],
            rmse=0.0,
            index=2,
        ),
        FrameDiff(
            frame_a=sample_frames[3],
            frame_b=sample_frames[4],
            rmse=0.82,
            index=3,
        ),
    ]
