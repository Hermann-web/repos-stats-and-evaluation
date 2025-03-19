import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import git
import pytest


@pytest.fixture(scope="session")
def sample_repo_fixture():
    """
    Create a more complex sample repository for testing.
    This fixture has a longer lifespan (session scope) to be reused across multiple tests.
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Initialize a Git repository
    repo = git.Repo.init(temp_dir)

    # Create a more complex directory structure
    # src directory with Python files
    src_dir = os.path.join(temp_dir, "src")
    os.makedirs(src_dir)

    # Create a Python file in src
    with open(os.path.join(src_dir, "main.py"), "w") as f:
        f.write(
            "def main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()\n"
        )

    # Create another Python file in src
    with open(os.path.join(src_dir, "utils.py"), "w") as f:
        f.write(
            "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n"
        )

    # Create a tests directory
    tests_dir = os.path.join(temp_dir, "tests")
    os.makedirs(tests_dir)

    # Create a test file
    with open(os.path.join(tests_dir, "test_utils.py"), "w") as f:
        f.write(
            "from src.utils import add, subtract\n\ndef test_add():\n    assert add(1, 2) == 3\n\ndef test_subtract():\n    assert subtract(5, 3) == 2\n"
        )

    # Create a docs directory
    docs_dir = os.path.join(temp_dir, "docs")
    os.makedirs(docs_dir)

    # Create a README.md file
    with open(os.path.join(temp_dir, "README.md"), "w") as f:
        f.write("# Sample Repository\n\nThis is a sample repository for testing.\n")

    # Create a requirements.txt file
    with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
        f.write("pytest==7.3.1\npandas==2.0.0\n")

    # Create a .gitignore file
    with open(os.path.join(temp_dir, ".gitignore"), "w") as f:
        f.write("__pycache__/\n*.py[cod]\n*$py.class\n.env\n.venv\n")

    # Add all files to the repository
    repo.git.add(all=True)
    repo.git.config("user.email", "test@example.com")
    repo.git.config("user.name", "Test User")
    repo.git.commit("-m", "Initial commit")

    # Create a new branch
    repo.git.checkout("-b", "feature/new-feature")

    # Add a new file in the feature branch
    with open(os.path.join(src_dir, "feature.py"), "w") as f:
        f.write("def new_feature():\n    return 'This is a new feature!'\n")

    # Commit the new file
    repo.git.add(all=True)
    repo.git.commit("-m", "Add new feature")

    # Switch back to the main branch
    repo.git.checkout("master")

    # Create some more commits on the main branch
    for i in range(3):
        with open(os.path.join(temp_dir, f"file{i}.txt"), "w") as f:
            f.write(f"This is file {i}.\n")
        repo.git.add(all=True)
        repo.git.commit("-m", f"Add file {i}")

    # Create a commit with a different author
    repo.git.config("user.email", "another@example.com")
    repo.git.config("user.name", "Another User")
    with open(os.path.join(temp_dir, "another_file.txt"), "w") as f:
        f.write("This file was created by another user.\n")
    repo.git.add(all=True)
    repo.git.commit("-m", "Add another file")

    yield temp_dir

    # Clean up temporary directory after test
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_report():
    """Create a sample report for testing."""
    return RepoReport(
        repository="test-repo",
        repository_url="https://github.com/user/test-repo.git",
        generated_at=datetime.now(timezone.utc),
        basic_stats=BasicStats(
            total_commits=10,
            active_branches=2,
            contributors=2,
            last_commit=datetime.now(timezone.utc),
            repo_size_mb=1.5,
        ),
        file_stats=FileStats(
            file_types={".py": 5, ".md": 2, ".txt": 3}, total_files=10, total_lines=150
        ),
        recent_activity=RecentActivity(
            total_recent_commits=5,
            avg_commits_per_day=2.5,
            max_commits_in_day=3,
            most_active_authors={"Test User": 3, "Another User": 2},
        ),
        commit_history=[
            CommitEntry(
                date=datetime.now(timezone.utc),
                author_email="test@example.com",
                author_name="Test User",
                message="Test commit",
                files_changed=2,
            )
        ],
        file_structure=FileStructure(
            structure={
                "test-repo": {"src": {"main.py": "main.py"}, "README.md": "README.md"}
            },
            excluded_patterns=[".git"],
            max_depth=2,
        ),
    )


# Import the classes needed for fixtures
from src.repo_stats import (
    BasicStats,
    CommitEntry,
    FileStats,
    FileStructure,
    RecentActivity,
    RepoReport,
    RepoStats,
)
