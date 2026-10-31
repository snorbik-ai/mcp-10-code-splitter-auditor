"""Façade SDK Python in-process pour l'audit et le découpage de code."""
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Set

# Inclusion de la racine de l'outil dans sys.path
_TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

from code_splitter_core.application.file_scanner import FileScannerService
from code_splitter_core.application.blueprint_generator import BlueprintGeneratorService
from code_splitter_core.domain.rules import (
    DEFAULT_WARN_THRESHOLD,
    DEFAULT_CRITICAL_THRESHOLD,
    DEFAULT_EXTENSIONS,
)


class CodeSplitterSDK:
    """SDK in-process pour l'audit des fichiers lourds et la génération de blueprints."""

    def __init__(self):
        self.scanner = FileScannerService()
        self.generator = BlueprintGeneratorService()

    def audit_code_weight(
        self,
        target_dir: Optional[str] = None,
        warn_threshold: int = DEFAULT_WARN_THRESHOLD,
        critical_threshold: int = DEFAULT_CRITICAL_THRESHOLD,
        extensions: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """Scanne le répertoire cible et renvoie le dictionnaire du rapport d'audit."""
        root = target_dir or str(Path.cwd())
        report = self.scanner.audit_directory(
            target_dir=root,
            warn_threshold=warn_threshold,
            critical_threshold=critical_threshold,
            extensions=extensions or DEFAULT_EXTENSIONS,
        )
        return report.model_dump()

    def generate_split_blueprint(self, file_path: str) -> Dict[str, Any]:
        """Génère un plan de découpage complet pour le fichier spécifié."""
        plan = self.generator.generate_plan(file_path)
        return plan.model_dump()
