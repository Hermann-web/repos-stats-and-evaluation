import os
import re
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import git
import pandas as pd
import pytest

from src.repo_stats import (
    BasicStats,
    CommitEntry,
    FileStats,
    FileStructure,
    RecentActivity,
    RepoReport,
    RepoStats,
    parse_byte_message,
)


class TestRepoStatsEdgeCases:
    @pytest.fixture
    def mock_repo(self) -> MagicMock:
        """Create a mock Git repository for testing edge cases."""
        mock_repo = MagicMock()
        mock_repo.working_tree_dir = "/mock/repo/path"

        # Mock head commit
        mock_commit = MagicMock()
        mock_commit.committed_datetime = datetime.now(timezone.utc)
        mock_commit.author.email = "test@example.com"
        mock_commit.author.name = "Test User"
        mock_commit.message = "Test commit"
        mock_commit.stats.files = {"file1.txt": {"insertions": 10, "deletions": 5}}

        mock_repo.head.commit = mock_commit
        mock_repo.iter_commits.return_value = [mock_commit]
        mock_repo.heads = [MagicMock()]
        mock_repo.remotes.origin.url = "https://github.com/user/repo.git"

        return mock_repo

    def test_init_with_none_working_tree(self) -> None:
        """Test initialization with None working_tree_dir."""
        with patch("git.Repo") as mock_git_repo:
            mock_repo = mock_git_repo.return_value
            mock_repo.working_tree_dir = None

            with pytest.raises(ValueError, match="Invalid repository path*"):
                RepoStats("/path/to/repo")

    # def test_get_basic_stats_empty_repo(self, mock_repo):
    #     """Test getting basic statistics for an empty repository."""
    #     mock_repo.iter_commits.return_value = []

    #     with patch('git.Repo', return_value=mock_repo):
    #         repo_stats = RepoStats("/mock/repo/path")
    #         basic_stats = repo_stats.get_basic_stats()

    #         assert basic_stats.total_commits == 0
    #         assert basic_stats.contributors == 0

    def test_get_file_stats_empty_repo(self) -> None:
        """Test getting file statistics for an empty repository."""
        # Create an empty temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            # Initialize a Git repository without any files
            repo = git.Repo.init(temp_dir)

            # Set up the repository
            repo.git.config("user.email", "test@example.com")
            repo.git.config("user.name", "Test User")

            # Create the RepoStats object
            repo_stats = RepoStats(temp_dir)

            # Get the file statistics
            file_stats = repo_stats.get_file_stats()

            assert file_stats.total_files == 0
            assert file_stats.total_lines == 0
            assert file_stats.file_types == {}
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)

    # def test_get_commit_history_no_commits(self, mock_repo):
    #     """Test getting commit history with no commits."""
    #     mock_repo.iter_commits.return_value = []

    #     with patch('git.Repo', return_value=mock_repo):
    #         repo_stats = RepoStats("/mock/repo/path")

    #         # Define date range
    #         end_date = datetime.now(timezone.utc)
    #         start_date = end_date - timedelta(days=30)

    #         commit_history = repo_stats.get_commit_history(start_date, end_date)

    #         assert len(commit_history) == 0

    # def test_get_file_structure_permission_error(self)->None:
    #     """Test getting file structure with permission error."""
    #     with patch('pathlib.Path.iterdir', side_effect=PermissionError):
    #         repo_stats = MagicMock()
    #         repo_stats.working_tree_dir = "/mock/repo/path"

    #         # We need to patch the Path.is_file method to return False
    #         with patch('pathlib.Path.is_file', return_value=False):
    #             # Call the method directly to test the specific case
    #             result = RepoStats.get_file_structure(repo_stats)

    #             # The result should contain "Permission denied" for the root directory
    #             assert result[Path("/mock/repo/path").name] == "Permission denied"

    # def test_generate_report_no_commits(self, mock_repo):
    #     """Test generating a report with no commits."""
    #     mock_repo.iter_commits.return_value = []

    #     with patch('git.Repo', return_value=mock_repo):
    #         repo_stats = RepoStats("/mock/repo/path")

    #         # Define date range
    #         end_date = datetime.now(timezone.utc)
    #         start_date = end_date - timedelta(days=30)

    #         report = repo_stats.generate_report(start_date, end_date)

    #         assert report.recent_activity is None
    #         assert len(report.commit_history) == 0

    def test_non_utf8_files(self) -> None:
        """Test handling of non-UTF-8 encoded files."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            # Initialize a Git repository
            repo = git.Repo.init(temp_dir)

            # Create a file with non-UTF-8 content
            non_utf8_file = os.path.join(temp_dir, "non_utf8.txt")
            with open(non_utf8_file, "wb") as f:
                f.write(b"\x80\x81\x82\x83")  # Invalid UTF-8

            # Add the file to the repository
            repo.git.add(non_utf8_file)
            repo.git.config("user.email", "test@example.com")
            repo.git.config("user.name", "Test User")
            repo.git.commit("-m", "Add non-UTF-8 file")

            # Create the RepoStats object
            repo_stats = RepoStats(temp_dir)

            # Get the file statistics
            file_stats = repo_stats.get_file_stats()

            # The file should be counted but not included in line count
            assert file_stats.total_files == 1
            assert ".txt" in file_stats.file_types
            assert file_stats.file_types[".txt"] == 1
            # Line count should be 0 as the file can't be read as UTF-8
            assert file_stats.total_lines == 0
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)

    def test_parse_byte_message_unicode_error(self) -> None:
        """Test parsing byte messages with Unicode errors."""
        # Create a bytes object with invalid UTF-8
        invalid_bytes = b"\x80\x81\x82\x83"
        # The function should handle the UnicodeDecodeError and return an empty string
        result = parse_byte_message(invalid_bytes)
        assert result == ""
