import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class FileStructureAnalyzer:
    """A class to analyze and retrieve file structure from a directory."""

    # Define the TreeObject type
    TreeObject = str | dict[str, "TreeObject"]

    END_SIGNAL = "..."
    EXCLUDE_SIGNAL = ""

    def __init__(
        self,
        directory: str,
        max_depth: Optional[int] = None,
        exclude_patterns: Optional[List[str]] = None,
    ):
        """
        Initialize the FileStructureAnalyzer.

        Args:
            directory (str): The directory to analyze
            max_depth (int, optional): Maximum depth to traverse (None for unlimited)
            exclude_patterns (list, optional): List of regex patterns to exclude
        """
        self.directory = Path(directory)
        self.max_depth = max_depth
        self.exclude_patterns = exclude_patterns or []
        self.compiled_patterns = [
            re.compile(pattern) for pattern in self.exclude_patterns
        ]

    def should_exclude(self, path_str: str) -> bool:
        """
        Check if a path should be excluded based on the patterns.

        Args:
            path_str (str): The path string to check

        Returns:
            bool: True if the path should be excluded, False otherwise
        """
        for pattern in self.compiled_patterns:
            if pattern.search(path_str):
                return True
        return False

    def build_tree(self, path: Path, current_depth: int = 0) -> TreeObject:
        """
        Build a tree structure recursively from a path.

        Args:
            path (Path): The path to build the tree from
            current_depth (int): Current depth in the recursion

        Returns:
            TreeObject: A tree representation of the path
        """

        assert self.EXCLUDE_SIGNAL != self.END_SIGNAL

        if self.max_depth is not None and current_depth > self.max_depth:
            return self.END_SIGNAL

        path_str = str(path)
        if self.should_exclude(path_str):
            return self.EXCLUDE_SIGNAL

        if path.is_file():
            return str(path.name)

        result = {}
        try:
            for child in sorted(path.iterdir()):
                child_result = self.build_tree(child, current_depth + 1)
                if child_result != self.EXCLUDE_SIGNAL:
                    result[child.name] = child_result
        except PermissionError:
            return "Permission denied"

        return result

    def get_file_structure(self) -> Dict[str, TreeObject]:
        """
        Get the file structure of the directory.

        Returns:
            dict: A nested dictionary representing the file structure
        """
        tree = {self.directory.name: self.build_tree(self.directory)}
        return tree

    def get_formated_tree(self) -> tuple[dict[str, TreeObject], str, list[str]]:
        def format_tree(tree: dict[str, Any], indent: str = "") -> list[str]:
            result = []
            for i, (key, value) in enumerate(tree.items()):
                is_last = i == len(tree) - 1
                prefix = "└── " if is_last else "├── "

                if isinstance(value, dict):
                    result.append(f"{indent}{prefix}{key}/")
                    next_indent = indent + ("    " if is_last else "│   ")
                    result.extend(format_tree(value, next_indent))
                elif value == self.END_SIGNAL:
                    result.append(f"{indent}{prefix}{key}/ ...")
                else:
                    result.append(f"{indent}{prefix}{value}")
            return result

        tree = self.get_file_structure()
        raw_json = json.dumps(tree, indent=2)
        tree_view = format_tree(tree)

        return tree, raw_json, tree_view
