"""Tests for Markdown report generation."""

from pathlib import Path

from video_qa.config import AnalysisConfig
from video_qa.core.clusterer import Region
from video_qa.core.extractor import VideoMetadata
from video_qa.reporters.markdown import generate_report


def _make_metadata(tmp_path: Path) -> VideoMetadata:
    return VideoMetadata(
        duration=10.0,
        width=1920,
        height=1080,
        fps=30.0,
        has_audio=False,
        file_path=tmp_path / "test.mp4",
    )


def test_report_with_regions(
    sample_frames: list[Path],
    tmp_path: Path,
) -> None:
    metadata = _make_metadata(tmp_path)
    config = AnalysisConfig()
    regions = [
        Region(
            start_index=1,
            end_index=3,
            peak_index=2,
            before_frame=sample_frames[0],
            peak_frame=sample_frames[2],
            after_frame=sample_frames[4],
            max_rmse=0.82,
            timestamp_start=0.2,
            timestamp_end=0.6,
        ),
    ]
    report = generate_report(
        metadata,
        regions,
        config,
        tmp_path / "images",
    )
    assert "# Video QA Report: test.mp4" in report
    assert "1920x1080" in report
    assert "Region 1" in report
    assert "0.8200" in report
    assert "region_01.png" in report
    assert "video-qa" in report


def test_report_no_regions(tmp_path: Path) -> None:
    metadata = _make_metadata(tmp_path)
    config = AnalysisConfig()
    report = generate_report(metadata, [], config, tmp_path / "images")
    assert "No significant changes detected" in report
    assert "## Detected Regions" not in report
