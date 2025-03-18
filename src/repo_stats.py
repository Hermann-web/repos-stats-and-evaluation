import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import git
import pandas as pd


class RepoStats:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        self.repo_name = Path(self.repo.working_tree_dir).name

    def get_basic_stats(self):
        """Get basic repository statistics"""
        stats = {
            "total_commits": sum(1 for _ in self.repo.iter_commits()),
            "active_branches": len(list(self.repo.heads)),
            "contributors": len(set(c.author.email for c in self.repo.iter_commits())),
            "last_commit": self.repo.head.commit.committed_datetime,
            "repo_size_mb": self._get_repo_size(),
        }
        return stats

    def get_file_stats(self):
        """Get statistics about files in the repository"""
        file_counts = defaultdict(int)
        total_lines = 0

        for root, _, files in os.walk(self.repo.working_tree_dir):
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

        return {
            "file_types": dict(file_counts),
            "total_files": sum(file_counts.values()),
            "total_lines": total_lines,
        }

    def get_commit_history(self, start_date, end_date):
        """Get commit statistics for the last N days"""

        commits = []
        for commit in self.repo.iter_commits():
            if (
                commit.committed_datetime < start_date
                and commit.committed_datetime > end_date
            ):
                break
            commits.append(
                {
                    "date": commit.committed_datetime,
                    "author": commit.author.email,
                    "author_name": commit.author.name,
                    "message": commit.message,
                    "files_changed": len(commit.stats.files),
                }
            )

        df = pd.DataFrame(commits)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"], utc=True)
            df["date_only"] = df["date"].dt.date
            return df
        return pd.DataFrame()

    def _get_repo_size(self):
        """Calculate repository size in MB"""
        total_size = 0
        for root, _, files in os.walk(self.repo.working_tree_dir):
            total_size += sum(
                os.path.getsize(os.path.join(root, name)) for name in files
            )
        return round(total_size / (1024 * 1024), 2)  # Convert to MB

    def generate_report(self, start_date, end_date):
        """Generate a complete repository statistics report"""
        commit_history_df = self.get_commit_history(
            start_date=start_date, end_date=end_date
        )

        # Calculate activity metrics
        recent_activity = {}
        if not commit_history_df.empty:
            commits_by_day = commit_history_df.groupby("date_only").size()
            recent_activity = {
                "total_recent_commits": len(commit_history_df),
                "avg_commits_per_day": round(commits_by_day.mean(), 2),
                "max_commits_in_day": commits_by_day.max(),
                "most_active_authors": commit_history_df["author_name"]
                .value_counts()
                .head(5)
                .to_dict(),
            }

        report = {
            "repository": self.repo_name,
            "generated_at": datetime.now(),
            "basic_stats": self.get_basic_stats(),
            "file_stats": self.get_file_stats(),
            "recent_activity": recent_activity,
            "commit_history_df": commit_history_df,
        }
        return report
