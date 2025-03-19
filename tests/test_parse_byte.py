import pytest

from src.repo_stats import parse_byte_message


def test_parse_byte_message_string() -> None:
    """Test parsing a string message."""
    result = parse_byte_message("Hello, World!")
    assert result == "Hello, World!"


def test_parse_byte_message_bytes() -> None:
    """Test parsing a bytes message."""
    result = parse_byte_message(b"Hello, World!")
    assert result == "Hello, World!"


def test_parse_byte_message_none() -> None:
    """Test parsing a None message."""
    result = parse_byte_message(None)
    assert result == ""


def test_parse_byte_message_empty() -> None:
    """Test parsing an empty message."""
    result = parse_byte_message("")
    assert result == ""
    result = parse_byte_message(b"")
    assert result == ""


def test_parse_byte_message_special_chars() -> None:
    """Test parsing a message with special characters."""
    result = parse_byte_message("Hello, 世界!")
    assert result == "Hello, 世界!"
    result = parse_byte_message(
        b"Hello, \xe4\xb8\x96\xe7\x95\x8c!"
    )  # UTF-8 encoded "世界"
    assert result == "Hello, 世界!"
