from typing import Annotated

from pydantic import BaseModel, Field

Score10 = Annotated[int, Field(ge=0, le=10)]
Score5 = Annotated[int, Field(ge=0, le=5)]
Score15 = Annotated[int, Field(ge=0, le=15)]
Score1 = Annotated[int, Field(ge=0, le=1)]


class StructureProjetDesign(BaseModel):
    """Évalue la structure, la lisibilité et les pratiques de codage du projet."""

    architecture_modulaire: Score10 = Field(
        ..., description="Séparation claire des composants."
    )
    architecture_modulaire_comment: str = ""

    lisibilite_code: Score5 = Field(
        ..., description="Clarté des noms, commentaires, indentation."
    )
    lisibilite_code_comment: str = ""

    refactorisation: Score5 = Field(
        ..., description="Absence de duplication, fonctions lisibles."
    )
    refactorisation_comment: str = ""

    tests_unitaires: Score10 = Field(..., description="Présence et qualité des tests.")
    tests_unitaires_comment: str = ""

    environnement_virtuel: Score10 = Field(
        ..., description="Usage correct de l’environnement virtuel."
    )
    environnement_virtuel_comment: str = ""


class CollaborationQualite(BaseModel):
    """Évalue la collaboration à travers Git et la répartition du travail."""

    git_utilisation: Score10 = Field(
        ..., description="Commits cohérents, messages clairs."
    )
    git_utilisation_comment: str = ""

    repartition_taches: Score15 = Field(
        ..., description="Répartition équilibrée des tâches."
    )
    repartition_taches_comment: str = ""


class DocumentationLivrables(BaseModel):
    """Évalue la qualité de la documentation, la structure du dépôt, et le prompt engineering."""

    readme: Score10 = Field(..., description="README détaillé.")
    readme_comment: str = ""

    code_commente: Score5 = Field(
        ..., description="Commentaires et docstrings pertinents."
    )
    code_commente_comment: str = ""

    guide_utilisation: Score5 = Field(
        ..., description="Instructions de lancement claires."
    )
    guide_utilisation_comment: str = ""

    livrables_propres: Score5 = Field(
        ..., description="Dépôt propre, sans fichiers parasites."
    )
    livrables_propres_comment: str = ""

    prompt_engineering: Score10 = Field(..., description="Prompt clair et pertinent.")
    prompt_engineering_comment: str = ""


class BonusML(BaseModel):
    """Critères bonus pour approfondissements ML."""

    choix_modele: Score1 = Field(..., description="Choix du modèle adapté.")
    choix_modele_comment: str = ""

    pretraitement: Score1 = Field(..., description="Prétraitement pertinent.")
    pretraitement_comment: str = ""

    evaluation_modele: Score1 = Field(..., description="Évaluation rigoureuse.")
    evaluation_modele_comment: str = ""

    analyse_critique: Score1 = Field(..., description="Analyse des performances.")
    analyse_critique_comment: str = ""

    shap_avance: Score1 = Field(
        ..., description="SHAP ou outil équivalent bien utilisé."
    )
    shap_avance_comment: str = ""


class BonusTechnique(BaseModel):
    """Critères bonus pour aspects techniques avancés."""

    pipeline_ml: Score1 = Field(..., description="Pipeline complet.")
    pipeline_ml_comment: str = ""

    shap_integre: Score1 = Field(..., description="SHAP intégré à l'interface.")
    shap_integre_comment: str = ""

    interface_fonctionnelle: Score1 = Field(
        ..., description="Interface utilisateur fonctionnelle."
    )
    interface_fonctionnelle_comment: str = ""

    complexite: Score1 = Field(
        ..., description="Fonctionnalités ou structure supplémentaires."
    )
    complexite_comment: str = ""

    dependances: Score1 = Field(..., description="Utilisation sobre des dépendances.")
    dependances_comment: str = ""


class EvaluationProjet(BaseModel):
    """Évaluation complète d’un projet encadré en Coding Week."""

    structure: StructureProjetDesign
    collaboration: CollaborationQualite
    documentation: DocumentationLivrables
    bonus_ml: BonusML
    bonus_tech: BonusTechnique
