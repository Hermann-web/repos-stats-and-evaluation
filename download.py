import logging
import sys
from pathlib import Path

sys.path.append(".")

from src.constants import DOWNLOADS_DIR, INPUT_FILE
from src.download_repos import (
    clone_or_update_repo,
    create_download_dir,
    read_repos_file,
)


def main() -> None:
    """Main function to process repositories."""
    create_download_dir(DOWNLOADS_DIR)
    repos = read_repos_file(INPUT_FILE)

    logging.info("Starting repository downloads...")

    for group_id, repo_url in repos.items():
        repo_name = Path(repo_url).stem.replace(".git", "")
        folder = DOWNLOADS_DIR / f"{group_id}-{repo_name}"
        clone_or_update_repo(repo_url, folder)
        logging.info("------------------------")

    logging.info("All repositories downloaded successfully!")


if __name__ == "__main__":
    main()
