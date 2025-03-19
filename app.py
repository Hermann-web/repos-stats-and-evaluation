import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px  # type: ignore
import streamlit as st

from src.utils import format_tree

sys.path.append(".")

from src.repo_stats import RepoReport, RepoStats


def find_repositories(base_path: str):
    """Find all git repositories in the given path"""
    return [str(path.parent) for path in Path(base_path).rglob(".git")]


def main() -> None:
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
        repo_paths = sorted(
            find_repositories(repo_base_path), key=lambda x: Path(x).name
        )
        if repo_paths:
            repo_names = [Path(path).name for path in repo_paths]
            selected_repo_index = st.sidebar.selectbox(
                "Select Repository",
                range(len(repo_names)),
                format_func=lambda i: repo_names[i],
            )

            st.sidebar.header("File Structure Options")
            show_file_structure = st.sidebar.checkbox("Show File Structure", value=True)
            max_depth = st.sidebar.slider(
                "Max Depth",
                min_value=0,
                max_value=10,
                value=3,
                help="Maximum directory depth to display (Set to 0 for full depth)",
            )
            exclude_patterns_input = st.sidebar.text_area(
                "Exclude Patterns (Regex, one per line)",
                value=".git\n__pycache__\n.pytest_cache\n.venv\nnode_modules",
                help="Regular expressions for paths to exclude, one per line",
            )
            exclude_patterns = [
                p.strip() for p in exclude_patterns_input.split("\n") if p.strip()
            ]

            st.sidebar.header("Date Range Options")

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

            # Display selected date range with better styling
            st.markdown(
                f"""
                <div style="padding: 10px; background-color: #f0f2f6; color:black; border-radius: 10px; text-align: center;">
                    <b>Date Range:</b> {start_date.strftime("%Y-%m-%d (%H:%M)")} → {end_date.strftime("%Y-%m-%d (%H:%M)")}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Analyze selected repository
            selected_repo_path = repo_paths[selected_repo_index]

            try:
                with st.spinner(
                    f"Analyzing repository: {repo_names[selected_repo_index]}..."
                ):
                    repo_stats = RepoStats(selected_repo_path)
                    report: RepoReport = repo_stats.generate_report(
                        start_date=start_date,
                        end_date=end_date,
                        max_depth=max_depth if max_depth > 0 else None,
                        exclude_patterns=exclude_patterns,
                    )

                # Display repository link with a nice button
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-top: 10px;">
                        <a href="{report.repository_url}" target="_blank" style="
                            background-color: #0078ff; 
                            color: white; 
                            padding: 10px 20px; 
                            border-radius: 5px; 
                            text-decoration: none; 
                            font-size: 16px;
                        ">Repository : {report.repository}</a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Display repository statistics
                col1, col2, col3 = st.columns([0.75, 0.75, 1.5])

                with col1:
                    st.header("Basic Statistics")
                    st.metric("Total Commits", report.basic_stats.total_commits)
                    st.metric("Active Branches", report.basic_stats.active_branches)
                    st.metric("Contributors", report.basic_stats.contributors)
                    st.metric(
                        "Last Commit",
                        report.basic_stats.last_commit.strftime("%Y-%m-%d %H:%M"),
                    )

                with col2:
                    st.header("File Statistics")

                    # Total files and lines
                    st.metric("Total Files", report.file_stats.total_files)
                    st.metric("Total Lines", report.file_stats.total_lines)
                    st.metric(
                        "Repository Size", f"{report.basic_stats.repo_size_mb} MB"
                    )

                with col3:
                    # File type distribution
                    file_types = report.file_stats.file_types
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

                if show_file_structure:
                    st.header("File Structure")

                    if report.file_structure:
                        structure = report.file_structure.structure

                        # Create tabs for different views
                        tab1, tab2 = st.tabs(["Tree View", "Raw JSON"])

                        with tab1:
                            if structure:
                                st.code("\n".join(format_tree(structure)), language="")
                            else:
                                st.info("No files found or all files were excluded")

                        with tab2:
                            st.code(json.dumps(structure, indent=2), language="json")

                        # Show exclusion information
                        if report.file_structure.excluded_patterns:
                            st.caption(
                                f"Excluded patterns: {', '.join(report.file_structure.excluded_patterns)}"
                            )
                        if report.file_structure.max_depth is not None:
                            st.caption(
                                f"Maximum depth: {report.file_structure.max_depth}"
                            )

                # Recent activity
                st.header("Recent Activity")

                if len(report.commit_history) == 0:
                    st.info(f"No commits found")
                else:
                    commit_df = pd.DataFrame(
                        [c.__dict__ for c in report.commit_history]
                    )
                    commit_df["date_only"] = pd.to_datetime(
                        commit_df["date"], utc=True
                    ).dt.date

                    commit_df["author"] = (
                        commit_df["author_name"]
                        + " <"
                        + commit_df["author_email"]
                        + ">"
                    )

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
                    author_df = commit_df["author"].value_counts().reset_index()
                    # author_df.columns = ["Author", "Commits"]
                    # set columns through a method

                    fig = px.bar(
                        author_df.head(10),
                        x="author",
                        y="count",
                        title="Top Contributors",
                        labels={"author": "Author", "count": "Number of Commits"},
                    )
                    st.plotly_chart(fig)

                    # Commit table
                    st.subheader("Recent Commits")
                    st.dataframe(
                        commit_df[["date", "author", "message", "files_changed"]]
                        .rename(
                            columns={
                                "date": "Date",
                                "author": "Author",
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
