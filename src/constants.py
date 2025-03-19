from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

# LOG_FOLDER = PROJECT_FOLDER / "logs"
# LOG_FOLDER.mkdir(exist_ok=True)
# LOG_FILE = LOG_FOLDER / "api.log"

# Define paths
DOWNLOADS_DIR = PROJECT_FOLDER / "downloads"

INPUT_FOLDER = PROJECT_FOLDER / "input"
INPUT_FILE = INPUT_FOLDER / "repos"
