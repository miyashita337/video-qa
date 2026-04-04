"""Configuration for video-qa analysis."""

from dataclasses import dataclass, field
from pathlib import Path

from video_qa.exceptions import InvalidInputError


@dataclass
class AnalysisConfig:
    """Configuration for a video analysis run."""

    fps: int = 5
    threshold: float = 0.05
    cluster_window: float = 2.0
    analyzer: str = "none"
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    output_format: str = "markdown"

    def __post_init__(self) -> None:
        if not 1 <= self.fps <= 60:
            raise InvalidInputError(f"fps must be 1-60, got {self.fps}")
        if not 0.0 < self.threshold <= 1.0:
            raise InvalidInputError(f"threshold must be 0.0-1.0, got {self.threshold}")
        if self.cluster_window <= 0:
            raise InvalidInputError(
                f"cluster_window must be positive, got {self.cluster_window}"
            )
        if self.analyzer not in ("none", "claude", "gemini"):
            raise InvalidInputError(
                f"analyzer must be none/claude/gemini, got {self.analyzer}"
            )
        if self.output_format not in ("markdown", "json"):
            raise InvalidInputError(
                f"output_format must be markdown/json, got {self.output_format}"
            )
