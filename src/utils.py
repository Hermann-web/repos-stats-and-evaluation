# Helper function to display the tree structure
from typing import Any


def format_tree(tree: dict[str, Any], indent: str = "") -> list[str]:
    result = []
    for i, (key, value) in enumerate(tree.items()):
        is_last = i == len(tree) - 1
        prefix = "└── " if is_last else "├── "

        if isinstance(value, dict):
            result.append(f"{indent}{prefix}{key}/")
            next_indent = indent + ("    " if is_last else "│   ")
            result.extend(format_tree(value, next_indent))
        elif value == "...":
            result.append(f"{indent}{prefix}{key}/ ...")
        else:
            result.append(f"{indent}{prefix}{value}")
    return result
