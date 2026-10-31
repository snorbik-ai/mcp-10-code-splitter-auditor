"""Règles et seuils du moteur d'audit de poids de code (Outil MCP #10).
Respect strict de la Règle d'Architecture n°5 du projet.
"""
from typing import Set

# Seuils canoniques de la charte de développement
DEFAULT_WARN_THRESHOLD: int = 250      # Seuil de vigilance / alerte
DEFAULT_CRITICAL_THRESHOLD: int = 350  # Seuil critique bloquant
IDEAL_MIN_LINES: int = 60              # Cible idéale basse
IDEAL_MAX_LINES: int = 240             # Cible idéale haute

# Extensions de fichiers de code auditées par défaut
DEFAULT_EXTENSIONS: Set[str] = {".py", ".ts", ".tsx", ".js", ".jsx"}

# Répertoires à exclure systématiquement pour éviter le bruit
IGNORED_DIRECTORIES: Set[str] = {
    ".git",
    "node_modules",
    ".pytest_cache",
    ".venv",
    "venv",
    "dist",
    "build",
    "__pycache__",
    ".next",
    ".idea",
    ".vscode",
    "dist_agents",
    "coverage",
    ".system_generated",
}
