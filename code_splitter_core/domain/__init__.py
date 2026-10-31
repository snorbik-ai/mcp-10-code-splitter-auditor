"""Domaine pour l'outil 10_code_splitter_auditor."""
from .entities import FileMetric, AuditReport, SplitSubModule, SplitPlan
from .rules import (
    DEFAULT_WARN_THRESHOLD,
    DEFAULT_CRITICAL_THRESHOLD,
    IDEAL_MIN_LINES,
    IDEAL_MAX_LINES,
    DEFAULT_EXTENSIONS,
    IGNORED_DIRECTORIES,
)

__all__ = [
    "FileMetric",
    "AuditReport",
    "SplitSubModule",
    "SplitPlan",
    "DEFAULT_WARN_THRESHOLD",
    "DEFAULT_CRITICAL_THRESHOLD",
    "IDEAL_MIN_LINES",
    "IDEAL_MAX_LINES",
    "DEFAULT_EXTENSIONS",
    "IGNORED_DIRECTORIES",
]
