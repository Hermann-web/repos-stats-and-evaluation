# ./app.py
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px  # type: ignore
import streamlit as st

sys.path.append(".")

from src.evaluation import (
    BonusML,
    BonusTechnique,
    CollaborationQualite,
    DocumentationLivrables,
    EvaluationProjet,
    StructureProjetDesign,
)
from src.project_eval import ProjectEvaluator
from src.repo_stats import RepoReport, RepoStats


def find_repositories(base_path: str):
    """Find all git repositories in the given path"""
    return [str(path.parent) for path in Path(base_path).rglob(".git")]


def render_evaluation_form(
    evaluator: ProjectEvaluator, current_evaluation: Optional[EvaluationProjet] = None
) -> bool:
    """Render the evaluation form in Streamlit."""
    st.header("📋 Project Evaluation")

    # Initialize with current evaluation or default
    if current_evaluation is None:
        current_evaluation = evaluator.create_default_evaluation()

    with st.form("evaluation_form"):
        st.subheader("🏗️ Structure & Project Design (40 points)")

        # Structure section
        col1, col2 = st.columns([1, 2])
        with col1:
            arch_mod = st.slider(
                "Architecture Modulaire",
                0,
                10,
                current_evaluation.structure.architecture_modulaire,
                key="arch_mod",
            )
        with col2:
            arch_mod_comment = st.text_area(
                "Comment",
                current_evaluation.structure.architecture_modulaire_comment,
                key="arch_mod_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            lisib_code = st.slider(
                "Lisibilité Code",
                0,
                5,
                current_evaluation.structure.lisibilite_code,
                key="lisib_code",
            )
        with col2:
            lisib_code_comment = st.text_area(
                "Comment",
                current_evaluation.structure.lisibilite_code_comment,
                key="lisib_code_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            refactor = st.slider(
                "Refactorisation",
                0,
                5,
                current_evaluation.structure.refactorisation,
                key="refactor",
            )
        with col2:
            refactor_comment = st.text_area(
                "Comment",
                current_evaluation.structure.refactorisation_comment,
                key="refactor_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            tests = st.slider(
                "Tests Unitaires",
                0,
                10,
                current_evaluation.structure.tests_unitaires,
                key="tests",
            )
        with col2:
            tests_comment = st.text_area(
                "Comment",
                current_evaluation.structure.tests_unitaires_comment,
                key="tests_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            env_virt = st.slider(
                "Environnement Virtuel",
                0,
                10,
                current_evaluation.structure.environnement_virtuel,
                key="env_virt",
            )
        with col2:
            env_virt_comment = st.text_area(
                "Comment",
                current_evaluation.structure.environnement_virtuel_comment,
                key="env_virt_comment",
            )

        st.subheader("🤝 Collaboration & Quality (25 points)")

        col1, col2 = st.columns([1, 2])
        with col1:
            git_util = st.slider(
                "Git Utilisation",
                0,
                10,
                current_evaluation.collaboration.git_utilisation,
                key="git_util",
            )
        with col2:
            git_util_comment = st.text_area(
                "Comment",
                current_evaluation.collaboration.git_utilisation_comment,
                key="git_util_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            repartition = st.slider(
                "Répartition Tâches",
                0,
                15,
                current_evaluation.collaboration.repartition_taches,
                key="repartition",
            )
        with col2:
            repartition_comment = st.text_area(
                "Comment",
                current_evaluation.collaboration.repartition_taches_comment,
                key="repartition_comment",
            )

        st.subheader("📚 Documentation & Deliverables (35 points)")

        col1, col2 = st.columns([1, 2])
        with col1:
            readme = st.slider(
                "README", 0, 10, current_evaluation.documentation.readme, key="readme"
            )
        with col2:
            readme_comment = st.text_area(
                "Comment",
                current_evaluation.documentation.readme_comment,
                key="readme_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            code_comment = st.slider(
                "Code Commenté",
                0,
                5,
                current_evaluation.documentation.code_commente,
                key="code_comment",
            )
        with col2:
            code_comment_comment = st.text_area(
                "Comment",
                current_evaluation.documentation.code_commente_comment,
                key="code_comment_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            guide_util = st.slider(
                "Guide Utilisation",
                0,
                5,
                current_evaluation.documentation.guide_utilisation,
                key="guide_util",
            )
        with col2:
            guide_util_comment = st.text_area(
                "Comment",
                current_evaluation.documentation.guide_utilisation_comment,
                key="guide_util_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            livrables = st.slider(
                "Livrables Propres",
                0,
                5,
                current_evaluation.documentation.livrables_propres,
                key="livrables",
            )
        with col2:
            livrables_comment = st.text_area(
                "Comment",
                current_evaluation.documentation.livrables_propres_comment,
                key="livrables_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            prompt_eng = st.slider(
                "Prompt Engineering",
                0,
                10,
                current_evaluation.documentation.prompt_engineering,
                key="prompt_eng",
            )
        with col2:
            prompt_eng_comment = st.text_area(
                "Comment",
                current_evaluation.documentation.prompt_engineering_comment,
                key="prompt_eng_comment",
            )

        st.subheader("🤖 Bonus ML (5 points)")

        col1, col2 = st.columns([1, 2])
        with col1:
            choix_modele = st.slider(
                "Choix Modèle",
                0,
                1,
                current_evaluation.bonus_ml.choix_modele,
                key="choix_modele",
            )
        with col2:
            choix_modele_comment = st.text_area(
                "Comment",
                current_evaluation.bonus_ml.choix_modele_comment,
                key="choix_modele_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            pretraitement = st.slider(
                "Prétraitement",
                0,
                1,
                current_evaluation.bonus_ml.pretraitement,
                key="pretraitement",
            )
        with col2:
            pretraitement_comment = st.text_area(
                "Comment",
                current_evaluation.bonus_ml.pretraitement_comment,
                key="pretraitement_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            eval_modele = st.slider(
                "Évaluation Modèle",
                0,
                1,
                current_evaluation.bonus_ml.evaluation_modele,
                key="eval_modele",
            )
        with col2:
            eval_modele_comment = st.text_area(
                "Comment",
                current_evaluation.bonus_ml.evaluation_modele_comment,
                key="eval_modele_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            analyse_crit = st.slider(
                "Analyse Critique",
                0,
                1,
                current_evaluation.bonus_ml.analyse_critique,
                key="analyse_crit",
            )
        with col2:
            analyse_crit_comment = st.text_area(
                "Comment",
                current_evaluation.bonus_ml.analyse_critique_comment,
                key="analyse_crit_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            shap_avance = st.slider(
                "SHAP Avancé",
                0,
                1,
                current_evaluation.bonus_ml.shap_avance,
                key="shap_avance",
            )
        with col2:
            shap_avance_comment = st.text_area(
                "Comment",
                current_evaluation.bonus_ml.shap_avance_comment,
                key="shap_avance_comment",
            )

        st.subheader("⚙️ Bonus Technique (5 points)")

        col1, col2 = st.columns([1, 2])
        with col1:
            pipeline_ml = st.slider(
                "Pipeline ML",
                0,
                1,
                current_evaluation.bonus_tech.pipeline_ml,
                key="pipeline_ml",
            )
        with col2:
            pipeline_ml_comment = st.text_area(
                "Comment",
                current_evaluation.bonus_tech.pipeline_ml_comment,
                key="pipeline_ml_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            shap_integre = st.slider(
                "SHAP Intégré",
                0,
                1,
                current_evaluation.bonus_tech.shap_integre,
                key="shap_integre",
            )
        with col2:
            shap_integre_comment = st.text_area(
                "Comment",
                current_evaluation.bonus_tech.shap_integre_comment,
                key="shap_integre_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            interface_fonc = st.slider(
                "Interface Fonctionnelle",
                0,
                1,
                current_evaluation.bonus_tech.interface_fonctionnelle,
                key="interface_fonc",
            )
        with col2:
            interface_fonc_comment = st.text_area(
                "Comment",
                current_evaluation.bonus_tech.interface_fonctionnelle_comment,
                key="interface_fonc_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            complexite = st.slider(
                "Complexité",
                0,
                1,
                current_evaluation.bonus_tech.complexite,
                key="complexite",
            )
        with col2:
            complexite_comment = st.text_area(
                "Comment",
                current_evaluation.bonus_tech.complexite_comment,
                key="complexite_comment",
            )

        col1, col2 = st.columns([1, 2])
        with col1:
            dependances = st.slider(
                "Dépendances",
                0,
                1,
                current_evaluation.bonus_tech.dependances,
                key="dependances",
            )
        with col2:
            dependances_comment = st.text_area(
                "Comment",
                current_evaluation.bonus_tech.dependances_comment,
                key="dependances_comment",
            )

        # Submit button
        submitted = st.form_submit_button("💾 Save Evaluation", type="primary")

        if submitted:
            # Create evaluation object
            new_evaluation = EvaluationProjet(
                structure=StructureProjetDesign(
                    architecture_modulaire=arch_mod,
                    architecture_modulaire_comment=arch_mod_comment,
                    lisibilite_code=lisib_code,
                    lisibilite_code_comment=lisib_code_comment,
                    refactorisation=refactor,
                    refactorisation_comment=refactor_comment,
                    tests_unitaires=tests,
                    tests_unitaires_comment=tests_comment,
                    environnement_virtuel=env_virt,
                    environnement_virtuel_comment=env_virt_comment,
                ),
                collaboration=CollaborationQualite(
                    git_utilisation=git_util,
                    git_utilisation_comment=git_util_comment,
                    repartition_taches=repartition,
                    repartition_taches_comment=repartition_comment,
                ),
                documentation=DocumentationLivrables(
                    readme=readme,
                    readme_comment=readme_comment,
                    code_commente=code_comment,
                    code_commente_comment=code_comment_comment,
                    guide_utilisation=guide_util,
                    guide_utilisation_comment=guide_util_comment,
                    livrables_propres=livrables,
                    livrables_propres_comment=livrables_comment,
                    prompt_engineering=prompt_eng,
                    prompt_engineering_comment=prompt_eng_comment,
                ),
                bonus_ml=BonusML(
                    choix_modele=choix_modele,
                    choix_modele_comment=choix_modele_comment,
                    pretraitement=pretraitement,
                    pretraitement_comment=pretraitement_comment,
                    evaluation_modele=eval_modele,
                    evaluation_modele_comment=eval_modele_comment,
                    analyse_critique=analyse_crit,
                    analyse_critique_comment=analyse_crit_comment,
                    shap_avance=shap_avance,
                    shap_avance_comment=shap_avance_comment,
                ),
                bonus_tech=BonusTechnique(
                    pipeline_ml=pipeline_ml,
                    pipeline_ml_comment=pipeline_ml_comment,
                    shap_integre=shap_integre,
                    shap_integre_comment=shap_integre_comment,
                    interface_fonctionnelle=interface_fonc,
                    interface_fonctionnelle_comment=interface_fonc_comment,
                    complexite=complexite,
                    complexite_comment=complexite_comment,
                    dependances=dependances,
                    dependances_comment=dependances_comment,
                ),
            )

            # Save evaluation
            print(f"***########Saving evaluation: {new_evaluation}")
            if evaluator.save_evaluation(new_evaluation):
                st.success("✅ Evaluation saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save evaluation")

    return submitted


def render_evaluation_display(
    evaluator: ProjectEvaluator, evaluation: EvaluationProjet
):
    """Display evaluation results and scores."""
    st.header("📊 Evaluation Results")

    # Calculate scores
    scores = evaluator.calculate_scores(evaluation)

    # Display score summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Main Score",
            f"{scores['main_score']}/{scores['main_max']}",
            f"{scores['percentage']}%",
        )

    with col2:
        st.metric("Bonus Score", f"{scores['total_bonus']}/{scores['total_bonus_max']}")

    with col3:
        st.metric("Final Score", f"{scores['final_score']}/{scores['final_max']}")

    with col4:
        grade = (
            "A"
            if scores["percentage"] >= 90
            else "B"
            if scores["percentage"] >= 80
            else "C"
            if scores["percentage"] >= 70
            else "D"
            if scores["percentage"] >= 60
            else "F"
        )
        st.metric("Grade", grade)

    # Score breakdown chart
    breakdown_data = {
        "Category": [
            "Structure\n& Design",
            "Collaboration",
            "Documentation",
            "ML Bonus",
            "Tech Bonus",
        ],
        "Score": [
            scores["structure_score"],
            scores["collaboration_score"],
            scores["documentation_score"],
            scores["bonus_ml_score"],
            scores["bonus_tech_score"],
        ],
        "Max": [
            scores["structure_max"],
            scores["collaboration_max"],
            scores["documentation_max"],
            scores["bonus_ml_max"],
            scores["bonus_tech_max"],
        ],
    }

    df = pd.DataFrame(breakdown_data)
    df["Percentage"] = (df["Score"] / df["Max"] * 100).round(1)

    fig = px.bar(
        df,
        x="Category",
        y="Score",
        text="Score",
        title="Score Breakdown by Category",
        color="Percentage",
        color_continuous_scale="RdYlGn",
    )
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Display summary
    summary = evaluator.get_evaluation_summary(evaluation)
    st.markdown(summary)


def main() -> None:
    query_params = st.query_params
    repo_from_url = query_params.get("repo", None)

    print(f"Query params: {query_params}")
    print(f"Selected repo from URL: {repo_from_url}")

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
            # Get repo names
            repo_names = [Path(path).name for path in repo_paths]

            # Determine selected index from URL
            selected_repo_index = 0
            if repo_from_url is not None:
                # If repo_from_url is provided, find its index
                if repo_from_url in repo_names:
                    selected_repo_index = repo_names.index(repo_from_url)
                else:
                    st.sidebar.warning(
                        f"Repository '{repo_from_url}' not found in the list."
                    )

            # Selectbox
            selected_repo_index = st.sidebar.selectbox(
                "Select Repository",
                range(len(repo_names)),
                index=selected_repo_index,
                format_func=lambda i: repo_names[i],
            )

            # Sync to URL if user picks from selectbox
            selected_repo_name = repo_names[selected_repo_index]
            if selected_repo_name != repo_from_url:
                st.query_params["repo"] = selected_repo_name

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
                value=".DS_Store\n__pycache__\n.pytest_cache\n.venv\nnode_modules",
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

            with st.spinner(
                f"Analyzing repository: {repo_names[selected_repo_index]}..."
            ):
                repo_stats = RepoStats(selected_repo_path)
                report: RepoReport = repo_stats.generate_report(
                    start_date=start_date,
                    end_date=end_date,
                    max_depth=max_depth,
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

            # Create tabs for different views
            tab1, tab2 = st.tabs(["📊 Repository Analysis", "📋 Project Evaluation"])

            with tab1:
                try:
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

                        structure_raw_json: str = (
                            report.file_structure.structure_raw_json
                        )
                        formated_tree: list[str] = (
                            report.file_structure.structure_formated
                        )

                        # Create tabs for different views
                        tab1_fs, tab2_fs = st.tabs(["Tree View", "Raw JSON"])

                        with tab1_fs:
                            if formated_tree:
                                st.code("\n".join(formated_tree), language="")
                            else:
                                st.info("No files found or all files were excluded")

                        with tab2_fs:
                            st.code(
                                structure_raw_json,
                                language="json",
                            )

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
                        activity_df["date_only"] = pd.to_datetime(
                            activity_df["date_only"]
                        )

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
                            title=f"Commit Activity",
                            labels={"date_only": "Date", "commits": "Commits"},
                        )
                        st.plotly_chart(fig)

                        # Author activity chart
                        author_df = commit_df["author"].value_counts().reset_index()

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

            with tab2:
                # Project Evaluation Tab
                try:
                    evaluator = ProjectEvaluator(selected_repo_path)

                    # Load existing evaluation
                    current_evaluation, is_valid, error_message = (
                        evaluator.load_evaluation()
                    )

                    # Show file status
                    if current_evaluation is None:
                        st.info(
                            "📄 No evaluation file found. A new evaluation.json will be created."
                        )
                        show_form = True
                    elif not is_valid:
                        st.warning(f"⚠️ Evaluation file is invalid: {error_message}")
                        st.info(
                            "Please fix the issues or use the form below to recreate the evaluation."
                        )
                        show_form = True
                    else:
                        st.success("✅ Valid evaluation file found!")
                        show_form = False

                        # Show current evaluation results
                        render_evaluation_display(evaluator, current_evaluation)

                        # Add button to edit evaluation
                        if st.button("✏️ Edit Evaluation"):
                            st.session_state.show_eval_form = True

                        if st.session_state.get("show_eval_form", False):
                            show_form = True

                    # Show form if needed
                    if show_form:
                        submitted = render_evaluation_form(
                            evaluator, current_evaluation
                        )
                        if submitted:
                            # Only reset form display state after successful submission
                            st.session_state.show_eval_form = False

                except Exception as e:
                    st.error(f"Error with evaluation: {str(e)}")
                    st.info(
                        "You can still create a new evaluation using the form below."
                    )

                    # Fallback: create evaluator with basic path
                    try:
                        evaluator = ProjectEvaluator(selected_repo_path)
                        render_evaluation_form(evaluator)
                    except Exception as fallback_e:
                        st.error(f"Cannot create evaluator: {str(fallback_e)}")

        else:
            st.sidebar.warning(f"No git repositories found in {repo_base_path}")
    else:
        st.sidebar.error(f"Path {repo_base_path} does not exist")


if __name__ == "__main__":
    main()
