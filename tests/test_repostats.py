import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Generator

import git
import pytest

from src.repo_stats import (
    BasicStats,
    CommitEntry,
    FileStats,
    FileStructure,
    RecentActivity,
    RepoReport,
    RepoStats,
    TreeObject,
    parse_byte_message,
)


class TestRepoStats:
    @pytest.fixture
    def temp_git_repo(self) -> Generator[str, Any, None]:
        """Create a temporary Git repository for testing."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()

        # Initialize a Git repository
        repo = git.Repo.init(temp_dir)

        # Create a test file
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("print('Hello, World!')\n")

        # Add test file to repository
        repo.git.add(test_file)
        repo.git.config("user.email", "test@example.com")
        repo.git.config("user.name", "Test User")
        repo.git.commit("-m", "Initial commit")

        # Create a second file
        test_file2 = os.path.join(temp_dir, "test2.txt")
        with open(test_file2, "w") as f:
            f.write("This is a test file.\n")

        # Add second file to repository
        repo.git.add(test_file2)
        repo.git.commit("-m", "Add second file")

        # Create a subdirectory
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)

        # Create a file in the subdirectory
        subdir_file = os.path.join(subdir, "subfile.md")
        with open(subdir_file, "w") as f:
            f.write("# Markdown File\n\nThis is a test markdown file.\n")

        # Add subdirectory file to repository
        repo.git.add(subdir_file)
        repo.git.commit("-m", "Add subdirectory file")

        yield temp_dir

        # Clean up temporary directory after test
        shutil.rmtree(temp_dir)

    def test_init(self, temp_git_repo: str) -> None:
        """Test the initialization of RepoStats."""
        repo_stats = RepoStats(temp_git_repo)
        assert repo_stats.repo_path == temp_git_repo
        assert repo_stats.working_tree_dir == temp_git_repo
        assert repo_stats.repo_name == Path(temp_git_repo).name
        assert isinstance(repo_stats.repo, git.Repo)

    def test_init_invalid_repo(self) -> None:
        """Test initialization with an invalid repository path."""
        with pytest.raises(ValueError):
            RepoStats("/tmp/nonexistent_repo")

    def test_get_basic_stats(self, temp_git_repo: str) -> None:
        """Test getting basic statistics."""
        repo_stats = RepoStats(temp_git_repo)
        basic_stats = repo_stats.get_basic_stats()

        assert isinstance(basic_stats, BasicStats)
        assert basic_stats.total_commits == 3  # We created 3 commits
        assert basic_stats.active_branches == 1  # Only master branch
        assert basic_stats.contributors == 1  # Only one contributor
        assert isinstance(basic_stats.last_commit, datetime)
        assert basic_stats.repo_size_mb > 0

    def test_get_file_stats(self, temp_git_repo: str) -> None:
        """Test getting file statistics."""
        repo_stats = RepoStats(temp_git_repo)
        file_stats = repo_stats.get_file_stats()

        assert isinstance(file_stats, FileStats)
        assert file_stats.total_files == 3  # We created 3 files
        assert file_stats.total_lines > 0
        assert ".py" in file_stats.file_types
        assert ".txt" in file_stats.file_types
        assert ".md" in file_stats.file_types
        assert file_stats.file_types[".py"] == 1
        assert file_stats.file_types[".txt"] == 1
        assert file_stats.file_types[".md"] == 1

    def test_get_commit_history(self, temp_git_repo: str) -> None:
        """Test getting commit history."""
        repo_stats = RepoStats(temp_git_repo)

        # Define date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)

        commit_history = repo_stats.get_commit_history(start_date, end_date)

        assert isinstance(commit_history, list)
        assert len(commit_history) > 0
        assert all(isinstance(entry, CommitEntry) for entry in commit_history)

        # Check first commit
        first_commit = commit_history[0]
        assert first_commit.author_name == "Test User"
        assert first_commit.author_email == "test@example.com"
        assert "Add subdirectory file" in first_commit.message
        assert first_commit.files_changed == 1

    def test_get_repo_size(self, temp_git_repo: str) -> None:
        """Test getting repository size."""
        repo_stats = RepoStats(temp_git_repo)
        repo_size = repo_stats._get_repo_size()

        assert isinstance(repo_size, float)
        assert repo_size > 0

    def test_get_file_structure(self, temp_git_repo: str) -> None:
        """Test getting file structure."""
        repo_stats = RepoStats(temp_git_repo)
        file_structure: dict[str, TreeObject] = repo_stats.get_file_structure()

        repo_name = Path(temp_git_repo).name
        assert isinstance(file_structure, dict)
        assert repo_name in file_structure

        # Check that the files we created are in the structure
        repo_contents = file_structure[repo_name]
        assert "test.py" in repo_contents
        assert "test2.txt" in repo_contents
        assert "subdir" in repo_contents
        assert "subfile.md" in repo_contents["subdir"]

    def test_get_file_structure_with_depth(self, temp_git_repo: str) -> None:
        """Test getting file structure with depth limit."""
        repo_stats = RepoStats(temp_git_repo)
        file_structure = repo_stats.get_file_structure(max_depth=0)

        repo_name = Path(temp_git_repo).name
        assert isinstance(file_structure, dict)
        assert repo_name in file_structure

        # At depth 0, we should only see the files in the root directory,
        # and directories should be marked with "..."
        repo_contents = file_structure[repo_name]
        assert isinstance(repo_contents, dict)
        assert "test.py" in repo_contents
        assert "test2.txt" in repo_contents
        assert "subdir" in repo_contents
        assert repo_contents["subdir"] == "..."

    def test_get_file_structure_with_exclude(self, temp_git_repo: str) -> None:
        """Test getting file structure with exclude patterns."""
        repo_stats = RepoStats(temp_git_repo)
        file_structure = repo_stats.get_file_structure(exclude_patterns=[".*\\.py$"])

        repo_name = Path(temp_git_repo).name
        assert isinstance(file_structure, dict)
        assert repo_name in file_structure

        # The .py file should be excluded
        repo_contents = file_structure[repo_name]
        assert isinstance(repo_contents, dict)
        assert "test.py" not in repo_contents
        assert "test2.txt" in repo_contents
        assert "subdir" in repo_contents

    def test_generate_report(self, temp_git_repo: str) -> None:
        """Test generating a complete report."""
        repo_stats = RepoStats(temp_git_repo)

        # Define date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)

        report = repo_stats.generate_report(
            start_date=start_date,
            end_date=end_date,
            max_depth=1,
            exclude_patterns=[".*\\.py$"],
        )

        assert isinstance(report, RepoReport)
        assert report.repository == Path(temp_git_repo).name
        assert isinstance(report.basic_stats, BasicStats)
        assert isinstance(report.file_stats, FileStats)
        assert isinstance(report.recent_activity, RecentActivity)
        assert isinstance(report.commit_history, list)
        assert isinstance(report.file_structure, FileStructure)

        # Check that the file structure is correct
        assert report.file_structure.max_depth == 1
        assert report.file_structure.excluded_patterns == [".*\\.py$"]

        # Check that the .py file is excluded
        repo_contents = report.file_structure.structure[Path(temp_git_repo).name]
        assert "test.py" not in repo_contents
        assert "test2.txt" in repo_contents
        assert "subdir" in repo_contents

    def test_parse_byte_message(self) -> None:
        """Test parsing byte messages."""

        # Test with a string
        assert parse_byte_message("test") == "test"

        # Test with bytes
        assert parse_byte_message(b"test") == "test"

        # # Test with None
        assert parse_byte_message(None) == ""
