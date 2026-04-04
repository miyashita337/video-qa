"""Tests for frame comparison and RMSE parsing."""

from video_qa.core.comparator import _parse_rmse


def test_parse_rmse_with_parentheses() -> None:
    # ImageMagick v7 format: "12345.6 (0.18834)"
    assert abs(_parse_rmse("12345.6 (0.18834)") - 0.18834) < 1e-6


def test_parse_rmse_normalized_only() -> None:
    # Just the normalized value
    assert abs(_parse_rmse("0.05123") - 0.05123) < 1e-6


def test_parse_rmse_zero() -> None:
    assert _parse_rmse("0 (0)") == 0.0


def test_parse_rmse_empty() -> None:
    assert _parse_rmse("") == 0.0


def test_parse_rmse_garbage() -> None:
    assert _parse_rmse("no numbers here") == 0.0


def test_parse_rmse_large_absolute_value() -> None:
    # Large absolute value without parens should be ignored (> 1.0)
    assert _parse_rmse("65535") == 0.0


def test_parse_rmse_multiline() -> None:
    output = "12345.6 (0.18834)\n0 (0)"
    assert abs(_parse_rmse(output) - 0.18834) < 1e-6
