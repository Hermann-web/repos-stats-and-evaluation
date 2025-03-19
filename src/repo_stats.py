import os
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TypeVar, Union

import git
import pandas as pd

TreeObject = TypeVar("T", bound=Union[str, dict[str, Any], None])


@dataclass
class BasicStats:
    total_commits: int
    active_branches: int
    contributors: int
    last_commit: datetime
    repo_size_mb: float


@dataclass
class FileStats:
    file_types: dict[str, int]
    total_files: int
    total_lines: int


@dataclass
class RecentActivity:
    total_recent_commits: int
    avg_commits_per_day: float
    max_commits_in_day: int
    most_active_authors: dict[str, int]


@dataclass
class CommitEntry:
    date: datetime
    author_email: str
    author_name: str
    message: str
    files_changed: int


@dataclass
class FileStructure:
    structure: dict[str, str | dict[str, Any] | None]
    excluded_patterns: list[str]
    max_depth: int | None


@dataclass
class RepoReport:
    repository: str
    repository_url: str
    generated_at: datetime
    basic_stats: BasicStats
    file_stats: FileStats
    recent_activity: RecentActivity | None
    commit_history: list[CommitEntry]
    file_structure: FileStructure | None = None


def parse_byte_message(text: str | bytes | None):
    if text is None:
        return ""
    if isinstance(text, bytes):
        try:
            return text.decode("utf-8")
        except UnicodeDecodeError:
            return ""
    return str(text)


class RepoStats:
    def __init__(self, repo_path: str):
        if not Path(repo_path).exists():
            raise ValueError(
                f"Invalid repository path: repo_path {repo_path} not found"
            )
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        if self.repo.working_tree_dir is None:
            raise ValueError(f"Invalid repository path: {repo_path}")
        self.working_tree_dir = self.repo.working_tree_dir
        self.repo_name = Path(self.working_tree_dir).name

    def get_basic_stats(self) -> BasicStats:
        return BasicStats(
            total_commits=sum(1 for _ in self.repo.iter_commits()),
            active_branches=len(list(self.repo.heads)),
            contributors=len(set(c.author.email for c in self.repo.iter_commits())),
            last_commit=self.repo.head.commit.committed_datetime,
            repo_size_mb=self._get_repo_size(),
        )

    def get_file_stats(self) -> FileStats:
        file_counts: dict[str, int] = defaultdict(int)
        total_lines = 0

        for root, _, files in os.walk(self.working_tree_dir):
            if ".git" in root:
                continue

            for file in files:
                ext = Path(file).suffix
                file_path = os.path.join(root, file)
                file_counts[ext or "no extension"] += 1

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        total_lines += sum(1 for _ in f)
                except:
                    pass

        return FileStats(
            file_types=dict(file_counts),
            total_files=sum(file_counts.values()),
            total_lines=total_lines,
        )

    def get_commit_history(self, start_date, end_date) -> list[CommitEntry]:
        commits = []
        for commit in self.repo.iter_commits():
            if (
                commit.committed_datetime < start_date
                and commit.committed_datetime > end_date
            ):
                break

            commits.append(
                CommitEntry(
                    date=commit.committed_datetime,
                    author_email=commit.author.email or "Unknown",
                    author_name=commit.author.name or "Unknown",
                    message=parse_byte_message(commit.message),
                    files_changed=len(commit.stats.files),
                )
            )
        return commits

    def _get_repo_size(self) -> float:
        total_size = 0
        for root, _, files in os.walk(self.working_tree_dir):
            total_size += sum(
                os.path.getsize(os.path.join(root, name))  # type: ignore
                for name in files
            )
        return round(total_size / (1024 * 1024), 2)  # Convert to MB

    def get_file_structure(
        self,
        max_depth: Optional[int] = None,
        exclude_patterns: Optional[list[str]] = None,
    ) -> dict[str, TreeObject]:
        """
        Get the file structure of the repository with options for depth control and exclusion patterns.

        Args:
            max_depth (int, optional): Maximum depth to traverse (None for unlimited)
            exclude_patterns (list, optional): List of regex patterns to exclude

        Returns:
            dict: A nested dictionary representing the file structure
        """

        exclude_patterns = exclude_patterns or []
        compiled_patterns = [re.compile(pattern) for pattern in exclude_patterns]

        def should_exclude(path_str: str) -> bool:
            for pattern in compiled_patterns:
                if pattern.search(path_str):
                    return True
            return False

        def build_tree(path: str, current_depth: int = 0) -> TreeObject:
            if max_depth is not None and current_depth > max_depth:
                return "..."

            path_str = str(path)
            if should_exclude(path_str):
                return None

            if path.is_file():
                return str(path.name)

            result = {}
            try:
                for child in sorted(path.iterdir()):
                    child_result = build_tree(child, current_depth + 1)
                    if child_result is not None:
                        result[child.name] = child_result
            except PermissionError:
                return "Permission denied"

            return result

        root_path = Path(self.working_tree_dir)
        tree: dict[str, TreeObject] = {root_path.name: build_tree(root_path)}
        return tree

    def generate_report(
        self, start_date, end_date, max_depth=None, exclude_patterns=None
    ) -> RepoReport:
        commit_history = self.get_commit_history(
            start_date=start_date, end_date=end_date
        )

        # Calculate activity metrics
        recent_activity = None
        if commit_history:
            df = pd.DataFrame([c.__dict__ for c in commit_history])
            df["date"] = pd.to_datetime(df["date"], utc=True)
            df["date_only"] = df["date"].dt.date
            commits_by_day = df.groupby("date_only").size()
            recent_activity = RecentActivity(
                total_recent_commits=len(commit_history),
                avg_commits_per_day=round(commits_by_day.mean(), 2),
                max_commits_in_day=commits_by_day.max(),
                most_active_authors=df["author_name"].value_counts().head(5).to_dict(),
            )

        # Get file structure with optional depth and exclusion patterns
        file_structure = FileStructure(
            structure=self.get_file_structure(
                max_depth=max_depth, exclude_patterns=exclude_patterns
            ),
            excluded_patterns=exclude_patterns or [],
            max_depth=max_depth,
        )

        return RepoReport(
            repository=self.repo_name,
            repository_url=self.repo.remotes.origin.url
            if hasattr(self.repo.remotes, "origin")
            else "no origin",
            generated_at=datetime.now(),
            basic_stats=self.get_basic_stats(),
            file_stats=self.get_file_stats(),
            recent_activity=recent_activity,
            commit_history=commit_history,
            file_structure=file_structure,
        )
