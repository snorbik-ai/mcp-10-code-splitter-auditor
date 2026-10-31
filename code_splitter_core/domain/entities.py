"""Modèles de domaine Pydantic pour l'audit et le plan de découpage (Outil MCP #10)."""
from typing import List, Optional
from pydantic import BaseModel, Field


class FileMetric(BaseModel):
    """Métrique d'un fichier source audité."""
    path: str
    relative_path: str
    line_count: int
    language: str
    status: str = Field(description="CONFORME (<=250), ALERTE (251-350) ou CRITIQUE (>350)")


class AuditReport(BaseModel):
    """Rapport synthétique et détaillé du scan de code."""
    total_files_scanned: int
    conform_count: int
    warn_count: int
    critical_count: int
    warn_threshold: int
    critical_threshold: int
    execution_ms: float
    heavy_files: List[FileMetric]


class SplitSubModule(BaseModel):
    """Définition d'un sous-fichier cible généré dans le plan de découpage."""
    file_name: str
    target_lines: int
    responsibility: str
    suggested_symbols: List[str]
    skeleton_code: str


class SplitPlan(BaseModel):
    """Plan de découpage exemplaire clé en main pour un fichier lourd."""
    original_file: str
    relative_path: str
    total_lines: int
    language: str
    pattern_type: str = Field(description="REACT_PARTIALS ou PYTHON_SUBMODULES")
    target_directory: str
    sub_modules: List[SplitSubModule]
    barrel_export_skeleton: str
    guidance_notes: List[str]
