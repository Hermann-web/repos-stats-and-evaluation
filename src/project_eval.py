# src/project_evaluator.py
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from src.evaluation import (
    BonusML,
    BonusTechnique,
    CollaborationQualite,
    DocumentationLivrables,
    EvaluationProjet,
    StructureProjetDesign,
)


class ProjectEvaluator:
    """Manages project evaluation JSON files and scoring calculations."""

    EVALUATION_FILENAME = "evaluation.json"

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.evaluation_file_path = self.repo_path / self.EVALUATION_FILENAME

    def load_evaluation(self) -> Tuple[Optional[EvaluationProjet], bool, str]:
        """
        Load evaluation from JSON file.

        Returns:
            Tuple of (evaluation_object, is_valid, error_message)
        """
        if not self.evaluation_file_path.exists():
            return None, False, "Evaluation file does not exist"

        try:
            with open(self.evaluation_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not data:
                return None, False, "Evaluation file is empty"

            # Validate and create evaluation object
            evaluation = EvaluationProjet(**data)
            return evaluation, True, ""

        except json.JSONDecodeError as e:
            return None, False, f"JSON parsing error: {str(e)}"
        except Exception as e:
            return None, False, f"Validation error: {str(e)}"

    def save_evaluation(self, evaluation: EvaluationProjet) -> bool:
        """
        Save evaluation to JSON file.

        Args:
            evaluation: EvaluationProjet object to save

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            eval_dict = (
                evaluation.model_dump()
            )  # or asdict(evaluation) if not using pydantic
            print(f"***Saving evaluation to {self.evaluation_file_path}")
            with open(self.evaluation_file_path, "w", encoding="utf-8") as f:
                json.dump(eval_dict, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving evaluation: {e}")
            return False

    def create_default_evaluation(self) -> EvaluationProjet:
        """Create a default evaluation with zero scores."""
        return EvaluationProjet(
            structure=StructureProjetDesign(
                architecture_modulaire=0,
                architecture_modulaire_comment="",
                lisibilite_code=0,
                lisibilite_code_comment="",
                refactorisation=0,
                refactorisation_comment="",
                tests_unitaires=0,
                tests_unitaires_comment="",
                environnement_virtuel=0,
                environnement_virtuel_comment="",
            ),
            collaboration=CollaborationQualite(
                git_utilisation=0,
                git_utilisation_comment="",
                repartition_taches=0,
                repartition_taches_comment="",
            ),
            documentation=DocumentationLivrables(
                readme=0,
                readme_comment="",
                code_commente=0,
                code_commente_comment="",
                guide_utilisation=0,
                guide_utilisation_comment="",
                livrables_propres=0,
                livrables_propres_comment="",
                prompt_engineering=0,
                prompt_engineering_comment="",
            ),
            bonus_ml=BonusML(
                choix_modele=0,
                choix_modele_comment="",
                pretraitement=0,
                pretraitement_comment="",
                evaluation_modele=0,
                evaluation_modele_comment="",
                analyse_critique=0,
                analyse_critique_comment="",
                shap_avance=0,
                shap_avance_comment="",
            ),
            bonus_tech=BonusTechnique(
                pipeline_ml=0,
                pipeline_ml_comment="",
                shap_integre=0,
                shap_integre_comment="",
                interface_fonctionnelle=0,
                interface_fonctionnelle_comment="",
                complexite=0,
                complexite_comment="",
                dependances=0,
                dependances_comment="",
            ),
        )

    def calculate_scores(self, evaluation: EvaluationProjet) -> Dict[str, Any]:
        """
        Calculate total scores and breakdown.

        Args:
            evaluation: EvaluationProjet object

        Returns:
            Dict containing score breakdown and totals
        """
        # Structure scores (max 40)
        structure_score = (
            evaluation.structure.architecture_modulaire
            + evaluation.structure.lisibilite_code
            + evaluation.structure.refactorisation
            + evaluation.structure.tests_unitaires
            + evaluation.structure.environnement_virtuel
        )

        # Collaboration scores (max 25)
        collaboration_score = (
            evaluation.collaboration.git_utilisation
            + evaluation.collaboration.repartition_taches
        )

        # Documentation scores (max 35)
        documentation_score = (
            evaluation.documentation.readme
            + evaluation.documentation.code_commente
            + evaluation.documentation.guide_utilisation
            + evaluation.documentation.livrables_propres
            + evaluation.documentation.prompt_engineering
        )

        # Main score (max 100)
        main_score = structure_score + collaboration_score + documentation_score

        # ML Bonus scores (max 5)
        bonus_ml_score = (
            evaluation.bonus_ml.choix_modele
            + evaluation.bonus_ml.pretraitement
            + evaluation.bonus_ml.evaluation_modele
            + evaluation.bonus_ml.analyse_critique
            + evaluation.bonus_ml.shap_avance
        )

        # Technical Bonus scores (max 5)
        bonus_tech_score = (
            evaluation.bonus_tech.pipeline_ml
            + evaluation.bonus_tech.shap_integre
            + evaluation.bonus_tech.interface_fonctionnelle
            + evaluation.bonus_tech.complexite
            + evaluation.bonus_tech.dependances
        )

        # Total bonus
        total_bonus = bonus_ml_score + bonus_tech_score

        # Final score
        final_score = main_score + total_bonus

        return {
            "structure_score": structure_score,
            "structure_max": 40,
            "collaboration_score": collaboration_score,
            "collaboration_max": 25,
            "documentation_score": documentation_score,
            "documentation_max": 35,
            "main_score": main_score,
            "main_max": 100,
            "bonus_ml_score": bonus_ml_score,
            "bonus_ml_max": 5,
            "bonus_tech_score": bonus_tech_score,
            "bonus_tech_max": 5,
            "total_bonus": total_bonus,
            "total_bonus_max": 10,
            "final_score": final_score,
            "final_max": 110,
            "percentage": round((main_score / 100) * 100, 1) if main_score > 0 else 0,
        }

    def get_evaluation_summary(self, evaluation: EvaluationProjet) -> str:
        """Generate a text summary of the evaluation."""
        scores = self.calculate_scores(evaluation)

        summary = f"""
## Evaluation Summary

**Main Score:** {scores["main_score"]}/{scores["main_max"]} ({scores["percentage"]}%)
**Bonus Score:** {scores["total_bonus"]}/{scores["total_bonus_max"]}
**Final Score:** {scores["final_score"]}/{scores["final_max"]}

### Breakdown:
- **Structure & Design:** {scores["structure_score"]}/{scores["structure_max"]}
- **Collaboration:** {scores["collaboration_score"]}/{scores["collaboration_max"]}
- **Documentation:** {scores["documentation_score"]}/{scores["documentation_max"]}
- **ML Bonus:** {scores["bonus_ml_score"]}/{scores["bonus_ml_max"]}
- **Technical Bonus:** {scores["bonus_tech_score"]}/{scores["bonus_tech_max"]}
        """.strip()

        return summary
