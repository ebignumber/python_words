"""Tests for the main module."""

import pytest

from python_words.main import main


def test_main(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that main prints the expected message."""
    main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello from python_words!"
