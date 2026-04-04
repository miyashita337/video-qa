"""Tests for time-based clustering logic."""

from pathlib import Path

from video_qa.core.clusterer import cluster_key_moments
from video_qa.core.comparator import FrameDiff


def test_no_key_moments_when_all_below_threshold(
    sample_frames: list[Path],
) -> None:
    diffs = [
        FrameDiff(sample_frames[0], sample_frames[1], 0.01, 0),
        FrameDiff(sample_frames[1], sample_frames[2], 0.02, 1),
    ]
    regions = cluster_key_moments(
        diffs,
        threshold=0.05,
        cluster_window=2.0,
        fps=5,
        all_frames=sample_frames,
    )
    assert regions == []


def test_single_key_moment_creates_one_region(
    sample_frames: list[Path],
) -> None:
    diffs = [
        FrameDiff(sample_frames[0], sample_frames[1], 0.01, 0),
        FrameDiff(sample_frames[1], sample_frames[2], 0.80, 1),
        FrameDiff(sample_frames[2], sample_frames[3], 0.01, 2),
    ]
    regions = cluster_key_moments(
        diffs,
        threshold=0.05,
        cluster_window=2.0,
        fps=5,
        all_frames=sample_frames,
    )
    assert len(regions) == 1
    assert regions[0].peak_index == 1
    assert regions[0].max_rmse == 0.80


def test_adjacent_moments_clustered(
    sample_diffs: list[FrameDiff],
    sample_frames: list[Path],
) -> None:
    # diffs at index 1 and 3, with cluster_window=2s and fps=5
    # frame distance = 2, window = 10 frames -> same cluster
    regions = cluster_key_moments(
        sample_diffs,
        threshold=0.05,
        cluster_window=2.0,
        fps=5,
        all_frames=sample_frames,
    )
    assert len(regions) == 1


def test_distant_moments_separate_regions(
    sample_frames: list[Path],
    tmp_path: Path,
) -> None:
    # Create more frames for wider separation
    from PIL import Image

    frames: list[Path] = []
    for i in range(20):
        img = Image.new("RGB", (64, 48), (i * 10, 0, 0))
        p = tmp_path / f"wide_{i:06d}.png"
        img.save(p)
        frames.append(p)

    diffs = [FrameDiff(frames[i], frames[i + 1], 0.01, i) for i in range(19)]
    # Put big changes far apart
    diffs[2] = FrameDiff(frames[2], frames[3], 0.90, 2)
    diffs[15] = FrameDiff(frames[15], frames[16], 0.85, 15)

    # cluster_window=1s at 5fps = 5 frame window
    regions = cluster_key_moments(
        diffs,
        threshold=0.05,
        cluster_window=1.0,
        fps=5,
        all_frames=frames,
    )
    assert len(regions) == 2
    assert regions[0].peak_index == 2
    assert regions[1].peak_index == 15


def test_edge_first_frame(
    sample_frames: list[Path],
) -> None:
    diffs = [
        FrameDiff(sample_frames[0], sample_frames[1], 0.90, 0),
        FrameDiff(sample_frames[1], sample_frames[2], 0.01, 1),
    ]
    regions = cluster_key_moments(
        diffs,
        threshold=0.05,
        cluster_window=2.0,
        fps=5,
        all_frames=sample_frames,
    )
    assert len(regions) == 1
    # Before frame should be clamped to index 0
    assert regions[0].before_frame == sample_frames[0]


def test_edge_last_frame(
    sample_frames: list[Path],
) -> None:
    last = len(sample_frames) - 1
    diffs = [
        FrameDiff(sample_frames[i], sample_frames[i + 1], 0.01, i) for i in range(last)
    ]
    diffs[-1] = FrameDiff(
        sample_frames[last - 1],
        sample_frames[last],
        0.90,
        last - 1,
    )
    regions = cluster_key_moments(
        diffs,
        threshold=0.05,
        cluster_window=2.0,
        fps=5,
        all_frames=sample_frames,
    )
    assert len(regions) == 1
    # After frame should be clamped to last index
    assert regions[0].after_frame == sample_frames[last]


def test_empty_diffs(sample_frames: list[Path]) -> None:
    regions = cluster_key_moments(
        [],
        threshold=0.05,
        cluster_window=2.0,
        fps=5,
        all_frames=sample_frames,
    )
    assert regions == []
