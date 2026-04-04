"""Time-based clustering of key moments into regions."""

from dataclasses import dataclass
from pathlib import Path

from video_qa.core.comparator import FrameDiff


@dataclass
class Region:
    """A detected change region with Before/Peak/After frames."""

    start_index: int
    end_index: int
    peak_index: int
    before_frame: Path
    peak_frame: Path
    after_frame: Path
    max_rmse: float
    timestamp_start: float
    timestamp_end: float


def cluster_key_moments(
    diffs: list[FrameDiff],
    threshold: float,
    cluster_window: float,
    fps: int,
    all_frames: list[Path],
) -> list[Region]:
    """Cluster key moments into regions.

    Args:
        diffs: Frame-to-frame RMSE diffs.
        threshold: RMSE threshold for key moment detection.
        cluster_window: Max seconds between moments in same region.
        fps: Frames per second used during extraction.
        all_frames: All extracted frame paths (for Before/After lookup).

    Returns:
        List of detected Regions sorted by timestamp.
    """
    # Filter key moments above threshold
    key_moments = [d for d in diffs if d.rmse >= threshold]
    if not key_moments:
        return []

    # Sort by index
    key_moments.sort(key=lambda d: d.index)

    # Group into clusters based on time proximity
    frame_window = int(cluster_window * fps)
    clusters: list[list[FrameDiff]] = []
    current_cluster: list[FrameDiff] = [key_moments[0]]

    for moment in key_moments[1:]:
        if moment.index - current_cluster[-1].index <= frame_window:
            current_cluster.append(moment)
        else:
            clusters.append(current_cluster)
            current_cluster = [moment]
    clusters.append(current_cluster)

    # Convert clusters to Regions
    max_frame_idx = len(all_frames) - 1
    regions: list[Region] = []

    for cluster in clusters:
        start_idx = cluster[0].index
        end_idx = cluster[-1].index + 1  # +1 for frame_b
        peak = max(cluster, key=lambda d: d.rmse)

        # Before: one frame before region start, clamped to 0
        before_idx = max(0, start_idx - 1)
        # After: one frame after region end, clamped to max
        after_idx = min(max_frame_idx, end_idx + 1)

        regions.append(
            Region(
                start_index=start_idx,
                end_index=end_idx,
                peak_index=peak.index,
                before_frame=all_frames[before_idx],
                peak_frame=all_frames[peak.index],
                after_frame=all_frames[after_idx],
                max_rmse=peak.rmse,
                timestamp_start=start_idx / fps,
                timestamp_end=end_idx / fps,
            )
        )

    return regions
