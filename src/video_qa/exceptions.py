"""Custom exceptions for video-qa."""


class VideoQAError(Exception):
    """Base exception for video-qa."""


class ExternalToolError(VideoQAError):
    """Raised when an external tool (ffmpeg, ImageMagick) fails."""

    def __init__(self, tool: str, message: str, returncode: int | None = None) -> None:
        self.tool = tool
        self.returncode = returncode
        super().__init__(f"{tool} failed: {message}")


class InvalidInputError(VideoQAError):
    """Raised when input validation fails."""


class FrameExtractionError(VideoQAError):
    """Raised when frame extraction fails."""
