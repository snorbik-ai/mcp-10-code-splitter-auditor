"""Service de scan et d'audit récursif du poids des fichiers de code."""
import time
from pathlib import Path
from typing import List, Optional, Set

from ..domain.entities import FileMetric, AuditReport
from ..domain.rules import (
    DEFAULT_WARN_THRESHOLD,
    DEFAULT_CRITICAL_THRESHOLD,
    DEFAULT_EXTENSIONS,
    IGNORED_DIRECTORIES,
)
from ..infrastructure.file_system import FileSystemGateway


class FileScannerService:
    """Scanne une arborescence pour recenser les fichiers de code et leur volume de lignes."""

    def __init__(self, file_system: Optional[FileSystemGateway] = None):
        self.fs = file_system or FileSystemGateway()

    def audit_directory(
        self,
        target_dir: str | Path,
        warn_threshold: int = DEFAULT_WARN_THRESHOLD,
        critical_threshold: int = DEFAULT_CRITICAL_THRESHOLD,
        extensions: Optional[Set[str]] = None,
        ignored_dirs: Optional[Set[str]] = None,
    ) -> AuditReport:
        """Exécute l'audit récursif du code et produit le rapport."""
        start_time = time.perf_counter()
        root_path = self.fs.normalize_path(str(target_dir))
        
        valid_exts = extensions or DEFAULT_EXTENSIONS
        skip_dirs = ignored_dirs or IGNORED_DIRECTORIES

        all_metrics: List[FileMetric] = []
        heavy_files: List[FileMetric] = []
        conform_count = 0
        warn_count = 0
        critical_count = 0

        for current_root, dir_names, file_names in self._walk_safe(root_path, skip_dirs):
            for file_name in file_names:
                suffix = Path(file_name).suffix.lower()
                if suffix not in valid_exts:
                    continue

                full_path = current_root / file_name
                try:
                    rel_path = str(full_path.relative_to(root_path)).replace("\\", "/")
                except ValueError:
                    rel_path = full_path.name

                lines = self.fs.count_lines(full_path)
                status = self._classify_status(lines, warn_threshold, critical_threshold)

                metric = FileMetric(
                    path=str(full_path).replace("\\", "/"),
                    relative_path=rel_path,
                    line_count=lines,
                    language=self._detect_language(suffix),
                    status=status,
                )

                all_metrics.append(metric)
                if status == "CRITIQUE":
                    critical_count += 1
                    heavy_files.append(metric)
                elif status == "ALERTE":
                    warn_count += 1
                    heavy_files.append(metric)
                else:
                    conform_count += 1

        # Tri décroissant des fichiers lourds par nombre de lignes
        heavy_files.sort(key=lambda m: m.line_count, reverse=True)
        execution_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return AuditReport(
            total_files_scanned=len(all_metrics),
            conform_count=conform_count,
            warn_count=warn_count,
            critical_count=critical_count,
            warn_threshold=warn_threshold,
            critical_threshold=critical_threshold,
            execution_ms=execution_ms,
            heavy_files=heavy_files,
        )

    def _walk_safe(self, root_path: Path, skip_dirs: Set[str]):
        """Générateur de parcours récursif filtrant les dossiers exclus."""
        import os
        for current_root_str, dir_names, file_names in os.walk(str(root_path)):
            # Modification in-place pour empêcher os.walk d'entrer dans les dossiers exclus
            dir_names[:] = [d for d in dir_names if d not in skip_dirs]
            yield Path(current_root_str), dir_names, file_names

    @staticmethod
    def _classify_status(lines: int, warn_th: int, crit_th: int) -> str:
        if lines > crit_th:
            return "CRITIQUE"
        if lines > warn_th:
            return "ALERTE"
        return "CONFORME"

    @staticmethod
    def _detect_language(suffix: str) -> str:
        mapping = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "react_tsx",
            ".js": "javascript",
            ".jsx": "react_jsx",
        }
        return mapping.get(suffix, "unknown")
