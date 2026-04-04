"""Tests for config validation."""

import pytest

from video_qa.config import AnalysisConfig
from video_qa.exceptions import InvalidInputError


def test_default_config() -> None:
    config = AnalysisConfig()
    assert config.fps == 5
    assert config.threshold == 0.05
    assert config.analyzer == "none"


def test_valid_custom_config() -> None:
    config = AnalysisConfig(fps=30, threshold=0.1, analyzer="claude")
    assert config.fps == 30
    assert config.threshold == 0.1


def test_fps_too_low() -> None:
    with pytest.raises(InvalidInputError, match="fps must be 1-60"):
        AnalysisConfig(fps=0)


def test_fps_too_high() -> None:
    with pytest.raises(InvalidInputError, match="fps must be 1-60"):
        AnalysisConfig(fps=61)


def test_threshold_zero() -> None:
    with pytest.raises(InvalidInputError, match="threshold"):
        AnalysisConfig(threshold=0.0)


def test_threshold_above_one() -> None:
    with pytest.raises(InvalidInputError, match="threshold"):
        AnalysisConfig(threshold=1.1)


def test_invalid_analyzer() -> None:
    with pytest.raises(InvalidInputError, match="analyzer"):
        AnalysisConfig(analyzer="gpt4")


def test_invalid_output_format() -> None:
    with pytest.raises(InvalidInputError, match="output_format"):
        AnalysisConfig(output_format="html")


def test_negative_cluster_window() -> None:
    with pytest.raises(InvalidInputError, match="cluster_window"):
        AnalysisConfig(cluster_window=-1.0)
