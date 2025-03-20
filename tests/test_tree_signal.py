from enum import Enum

from src.file_structure import TreeSignal

def test_tree_signal_is_str():
    """Ensure all enum values are strings."""
    for signal in TreeSignal:
        assert isinstance(signal.value, str), f"{signal} is not a string"

def test_tree_signal_has_unique_values():
    """Ensure all enum values are unique."""
    values = [signal.value for signal in TreeSignal]
    assert len(values) == len(set(values)), "Enum values are not unique"

def test_tree_signal_integrity():
    """Ensure the enum contains STOP, END, and EXCLUDE with different values."""
    assert hasattr(TreeSignal, "STOP"), "STOP is missing from TreeSignal"
    assert hasattr(TreeSignal, "END"), "END is missing from TreeSignal"
    assert hasattr(TreeSignal, "EXCLUDE"), "EXCLUDE is missing from TreeSignal"
    
    assert TreeSignal.STOP != TreeSignal.END != TreeSignal.EXCLUDE, "Enum values should be different"
