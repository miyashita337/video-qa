"""Video metadata extraction and frame extraction using ffprobe/ffmpeg."""

import json
from dataclasses import dataclass
from pathlib import Path

from video_qa._subprocess import run_command
from video_qa.exceptions import FrameExtractionError, InvalidInputError


@dataclass
class VideoMetadata:
    """Metadata extracted from a video file."""

    duration: float
    width: int
    height: int
    fps: float
    has_audio: bool
    file_path: Path


def get_video_metadata(video_path: Path) -> VideoMetadata:
    """Extract metadata from a video file using ffprobe."""
    if not video_path.exists():
        raise InvalidInputError(f"Video file not found: {video_path}")
    if video_path.suffix.lower() not in (".mp4", ".mov", ".avi", ".mkv", ".webm"):
        raise InvalidInputError(f"Unsupported video format: {video_path.suffix}")

    result = run_command(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ]
    )

    try:
        probe = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise FrameExtractionError(f"Failed to parse ffprobe output: {e}") from e

    video_stream = None
    has_audio = False
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == "video" and video_stream is None:
            video_stream = stream
        if stream.get("codec_type") == "audio":
            has_audio = True

    if video_stream is None:
        raise FrameExtractionError("No video stream found in file")

    # Parse fps from r_frame_rate (e.g. "30/1" or "30000/1001")
    r_frame_rate = video_stream.get("r_frame_rate", "0/1")
    num, den = r_frame_rate.split("/")
    fps = float(num) / float(den) if float(den) != 0 else 0.0

    duration = float(probe.get("format", {}).get("duration", 0))

    return VideoMetadata(
        duration=duration,
        width=int(video_stream.get("width", 0)),
        height=int(video_stream.get("height", 0)),
        fps=fps,
        has_audio=has_audio,
        file_path=video_path,
    )


def extract_frames(
    video_path: Path,
    output_dir: Path,
    fps: int,
) -> list[Path]:
    """Extract frames from a video at the specified fps.

    Returns a sorted list of extracted frame file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    pattern = str(output_dir / "frame_%06d.png")

    run_command(
        [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vf",
            f"fps={fps}",
            "-q:v",
            "2",
            pattern,
        ],
        timeout=300,
    )

    frames = sorted(output_dir.glob("frame_*.png"))
    if not frames:
        raise FrameExtractionError(
            f"No frames extracted from {video_path} at {fps} fps"
        )

    return frames
