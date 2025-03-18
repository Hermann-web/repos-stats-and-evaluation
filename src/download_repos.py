import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define paths
DOWNLOADS_DIR = Path("downloads")
INPUT_FILE = Path("repos")


def create_download_dir(directory: Path) -> None:
    """Create the downloads directory if it doesn't exist."""
    directory.mkdir(exist_ok=True)


def read_repos_file(file_path: Path) -> dict[str, str]:
    """Read repository URLs from the input file, ignoring empty lines and comments."""
    if not file_path.exists() or not file_path.is_file():
        logging.error(f"Error: {file_path} file not found!")
        logging.info(
            "Please create a file at %s with GitHub repository URLs, one per line.",
            file_path,
        )
        sys.exit(1)

    with file_path.open("r") as file:
        return {
            f"gr{i:02}": line.strip()
            for i, line in enumerate(file, start=1)
            if line.strip() and not line.startswith("#")
        }


def clone_or_update_repo(repo_url: str, folder: Path) -> None:
    """Clone or update a Git repository."""
    if folder.is_dir():
        logging.info("Repository %s already exists, updating...", folder.name)
        subprocess.run(["git", "-C", str(folder), "pull"], check=False)
    else:
        logging.info("Cloning %s into %s...", repo_url, folder)
        subprocess.run(["git", "clone", repo_url, str(folder)], check=False)


def main():
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
