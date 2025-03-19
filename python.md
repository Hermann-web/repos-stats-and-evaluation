# Git Repository Analyzer

A Python tool for analyzing Git repositories and generating comprehensive reports about their structure, history, and statistics.

## Features

- Basic repository statistics (commits, branches, contributors)
- File type analysis and line counts
- Recent activity tracking
- Commit history analysis
- File structure visualization
- Contributor insights

## Prerequisites

- Python 3.8+
- Git installed on your system

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management. Here's how to get started:

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone https://github.com/someusername/git-repo-analyzer.git
cd git-repo-analyzer
```

3. Create and activate a virtual environment with uv:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

4. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Usage

```python
from repo_stats import RepoStats

# Initialize analyzer
repo_analyzer = RepoStats("path/to/your/repo")

# Generate report
report = repo_analyzer.generate_report()

# Access various statistics
print(f"Total commits: {report.basic_stats.total_commits}")
print(f"Active branches: {report.basic_stats.active_branches}")
```

## Running Tests

Run tests using pytest:

```bash
uv pip install pytest
pytest tests/
```

## Why uv?

We recommend uv because it offers:
- Significantly faster package installation
- Reliable dependency resolution
- Built-in virtual environment management
- Binary package distribution
- Drop-in replacement for pip

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
