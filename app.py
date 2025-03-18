import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(".")

from src.repo_stats import RepoStats


def find_repositories(base_path):
    """Find all git repositories in the given path"""
    return [str(path.parent) for path in Path(base_path).rglob(".git")]


def main():
    end_date_default = datetime(2025, 3, 18, 23, 0, 0, tzinfo=timezone.utc)
    start_date_default = datetime(2025, 3, 7, 23, 0, 0, tzinfo=timezone.utc)

    st.set_page_config(
        page_title="Git Repository Analyzer", page_icon="📊", layout="wide"
    )

    # Application title
    st.title("Git Repository Analyzer")

    # Sidebar for repository selection
    st.sidebar.header("Repository Selection")

    # Input for repository path
    repo_base_path = st.sidebar.text_input(
        "Repository Base Path",
        value="./downloads",
        help="Path to the folder containing git repositories",
    )

    # Find repositories
    if os.path.exists(repo_base_path):
        repo_paths = find_repositories(repo_base_path)
        if repo_paths:
            repo_names = sorted([Path(path).name for path in repo_paths])
            selected_repo_index = st.sidebar.selectbox(
                "Select Repository",
                range(len(repo_names)),
                format_func=lambda i: repo_names[i],
            )

            start_date = st.sidebar.date_input(
                "Start Date", value=start_date_default.date()
            )
            end_date = st.sidebar.date_input("End Date", value=end_date_default.date())

            # Convert back to datetime with the default time
            start_date = datetime.combine(start_date, datetime.min.time()).replace(
                tzinfo=timezone.utc
            )
            end_date = datetime.combine(end_date, datetime.min.time()).replace(
                tzinfo=timezone.utc
            )

            st.write(
                f"Date Range: {start_date.strftime('%Y-%m-%d')} ----> {end_date.strftime('%Y-%m-%d')}"
            )

            # Analyze selected repository
            selected_repo_path = repo_paths[selected_repo_index]

            try:
                with st.spinner(
                    f"Analyzing repository: {repo_names[selected_repo_index]}..."
                ):
                    repo_stats = RepoStats(selected_repo_path)
                    report = repo_stats.generate_report(
                        start_date=start_date, end_date=end_date
                    )

                # Display repository statistics
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.header("Basic Statistics")
                    st.metric("Repository", report["repository"])
                    st.metric("Total Commits", report["basic_stats"]["total_commits"])
                    st.metric(
                        "Active Branches", report["basic_stats"]["active_branches"]
                    )
                    st.metric("Contributors", report["basic_stats"]["contributors"])
                    st.metric(
                        "Repository Size", f"{report['basic_stats']['repo_size_mb']} MB"
                    )
                    st.metric(
                        "Last Commit",
                        report["basic_stats"]["last_commit"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    )

                with col2:
                    st.header("File Statistics")

                    # File type distribution
                    file_types = report["file_stats"]["file_types"]
                    if file_types:
                        file_df = pd.DataFrame(
                            {
                                "Type": list(file_types.keys()),
                                "Count": list(file_types.values()),
                            }
                        ).sort_values("Count", ascending=False)

                        fig = px.pie(
                            file_df,
                            values="Count",
                            names="Type",
                            title="File Type Distribution",
                            hole=0.4,
                        )
                        st.plotly_chart(fig)

                    # Total files and lines
                    st.metric("Total Files", report["file_stats"]["total_files"])
                    st.metric("Total Lines", report["file_stats"]["total_lines"])

                # Recent activity
                st.header("Recent Activity")

                if report["commit_history_df"].empty:
                    st.info(f"No commits found")
                else:
                    commit_df = report["commit_history_df"]

                    # Commit activity chart
                    activity_df = (
                        commit_df.groupby("date_only")
                        .size()
                        .reset_index(name="commits")
                    )
                    activity_df["date_only"] = pd.to_datetime(activity_df["date_only"])

                    # Create a complete date range
                    date_range = pd.date_range(
                        start=start_date.date(), end=end_date.date(), freq="D"
                    )
                    complete_df = pd.DataFrame({"date_only": date_range})
                    complete_df = complete_df.merge(
                        activity_df, on="date_only", how="left"
                    ).fillna(0)

                    fig = px.bar(
                        complete_df,
                        x="date_only",
                        y="commits",
                        title=f"Commit Activity ()",
                        labels={"date_only": "Date", "commits": "Commits"},
                    )
                    st.plotly_chart(fig)

                    # Author activity chart
                    author_df = commit_df["author_name"].value_counts().reset_index()
                    author_df.columns = ["Author", "Commits"]

                    fig = px.bar(
                        author_df.head(10),
                        x="Author",
                        y="Commits",
                        title="Top Contributors",
                        labels={"Author": "Author", "Commits": "Number of Commits"},
                    )
                    st.plotly_chart(fig)

                    # Commit table
                    st.subheader("Recent Commits")
                    st.dataframe(
                        commit_df[["date", "author_name", "message", "files_changed"]]
                        .rename(
                            columns={
                                "date": "Date",
                                "author_name": "Author",
                                "message": "Message",
                                "files_changed": "Files Changed",
                            }
                        )
                        .sort_values("Date", ascending=False),
                        use_container_width=True,
                    )

            except Exception as e:
                st.error(f"Error analyzing repository: {str(e)}")
                raise
        else:
            st.sidebar.warning(f"No git repositories found in {repo_base_path}")
    else:
        st.sidebar.error(f"Path {repo_base_path} does not exist")


if __name__ == "__main__":
    main()
