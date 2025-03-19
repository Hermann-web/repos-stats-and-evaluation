import re
from pathlib import Path
from typing import Dict, List, Optional


class FileStructureAnalyzer:
    """A class to analyze and retrieve file structure from a directory."""

    # Define the TreeObject type
    TreeObject = str | dict[str, "TreeObject"]

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
        if self.max_depth is not None and current_depth > self.max_depth:
            return "..."

        path_str = str(path)
        if self.should_exclude(path_str):
            return ""

        if path.is_file():
            return str(path.name)

        result: Dict[str, FileStructureAnalyzer.TreeObject] = {}
        try:
            for child in sorted(path.iterdir()):
                child_result = self.build_tree(child, current_depth + 1)
                if child_result != "":
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
