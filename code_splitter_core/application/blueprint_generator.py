"""Générateur de Plan de Découpage Exemplaire (Blueprint Clé en Main)."""
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..domain.entities import SplitPlan, SplitSubModule
from ..infrastructure.file_system import FileSystemGateway


class BlueprintGeneratorService:
    """Analyse un fichier de code lourd et produit un plan de découpage exemplaire."""

    def __init__(self, file_system: Optional[FileSystemGateway] = None):
        self.fs = file_system or FileSystemGateway()

    def generate_plan(self, file_path_str: str) -> SplitPlan:
        """Produit le plan de découpage architectural adapté au langage du fichier."""
        target_path = self.fs.normalize_path(file_path_str)
        if not target_path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {file_path_str}")

        content, lines = self.fs.read_text_safe(target_path)
        total_lines = len(lines)
        suffix = target_path.suffix.lower()

        if suffix == ".py":
            return self._generate_python_blueprint(target_path, content, total_lines)
        elif suffix in {".tsx", ".ts", ".jsx", ".js"}:
            # Détection fine : React UI (JSX/TSX) vs Données pures / Catalogue (TS/JS sans balise)
            has_jsx = bool(re.search(r"<[A-Z][A-Za-z0-9]*|import\s+.*React|className=", content)) or suffix in {".tsx", ".jsx"}
            if not has_jsx and suffix in {".ts", ".js"}:
                return self._generate_data_blueprint(target_path, content, total_lines)
            return self._generate_react_blueprint(target_path, content, total_lines)
        else:
            return self._generate_generic_blueprint(target_path, content, total_lines)

    def _generate_python_blueprint(self, path: Path, content: str, total_lines: int) -> SplitPlan:
        """Génère un plan de découpage pour un module Python vers un sous-package."""
        stem = path.stem
        subpkg_name = f"{stem}_modules" if not stem.endswith("_modules") else stem
        target_dir = str(path.parent / subpkg_name).replace("\\", "/")

        classes = []
        functions = []
        try:
            tree = ast.parse(content)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    functions.append(node.name)
        except Exception:
            # Fallback regex si syntaxe non standard
            classes = re.findall(r"^class\s+([A-Za-z0-9_]+)", content, re.MULTILINE)
            functions = re.findall(r"^(?:async\s+)?def\s+([A-Za-z0-9_]+)", content, re.MULTILINE)

        sub_modules = [
            SplitSubModule(
                file_name="domain_models.py",
                target_lines=max(60, min(180, total_lines // 4)),
                responsibility="Entités métier, DTOs Pydantic et règles de validation",
                suggested_symbols=classes[:max(1, len(classes)//2)] or ["DataModel"],
                skeleton_code='"""Entités et modèles du sous-module."""\nfrom pydantic import BaseModel\n\n'
                              + "\n\n".join(f"class {c}(BaseModel):\n    pass" for c in classes[:2] or ["DataModel"]),
            ),
            SplitSubModule(
                file_name="core_engine.py",
                target_lines=max(80, min(200, total_lines // 3)),
                responsibility="Logique de calcul, algorithmes et fonctions principales",
                suggested_symbols=functions[:max(1, len(functions)//2)] or ["process_data"],
                skeleton_code='"""Moteur de traitement métier."""\n\n'
                              + "\n\n".join(f"def {f}():\n    pass" for f in functions[:2] or ["process_data"]),
            ),
            SplitSubModule(
                file_name="helpers.py",
                target_lines=max(50, min(150, total_lines // 4)),
                responsibility="Utilitaires, formatage et fonctions auxiliaires",
                suggested_symbols=functions[max(1, len(functions)//2):] or ["format_output"],
                skeleton_code='"""Fonctions utilitaires et aides de formatage."""\n\ndef helper():\n    pass\n',
            ),
        ]

        # Barrel export ré-exportant les symboles
        all_exports = classes + functions
        export_list_str = ", ".join(f'"{s}"' for s in all_exports[:10])
        barrel = (
            f'"""Sous-package modulaire {subpkg_name} — Façade de ré-exportation."""\n'
            f"from .domain_models import *\n"
            f"from .core_engine import *\n"
            f"from .helpers import *\n\n"
            f"__all__ = [{export_list_str}]\n"
        )

        return SplitPlan(
            original_file=str(path).replace("\\", "/"),
            relative_path=path.name,
            total_lines=total_lines,
            language="python",
            pattern_type="PYTHON_SUBMODULES",
            target_directory=target_dir,
            sub_modules=sub_modules,
            barrel_export_skeleton=barrel,
            guidance_notes=[
                "Conserver l'ancien fichier comme façade d'import (compatibilité ascendante) : 'from .subpkg import *'",
                "Chaque sous-module doit rester entre 60 et 200 lignes.",
                "Valider que tous les tests existants passent à 100% après le découpage.",
            ],
        )

    def _generate_react_blueprint(self, path: Path, content: str, total_lines: int) -> SplitPlan:
        """Génère un plan de découpage pour un composant React / TSX lourd (partials + hook)."""
        stem = path.stem
        comp_dir = str(path.parent / stem).replace("\\", "/")

        sub_modules = [
            SplitSubModule(
                file_name=f"use{stem}Controller.ts",
                target_lines=max(80, min(180, total_lines // 3)),
                responsibility="Custom Hook Contrôleur : gestion des états React, effets et handlers",
                suggested_symbols=[f"use{stem}Controller"],
                skeleton_code=f'import {{ useState, useCallback }} from "react";\n\n'
                              f"export const use{stem}Controller = () => {{\n"
                              f'  const [state, setState] = useState(null);\n'
                              f"  const handleAction = useCallback(() => {{}}, []);\n"
                              f"  return {{ state, handleAction }};\n}};\n",
            ),
            SplitSubModule(
                file_name=f"{stem}.tsx",
                target_lines=max(60, min(120, total_lines // 4)),
                responsibility="Composant Orchestrateur léger assemblant les partials",
                suggested_symbols=[stem],
                skeleton_code=f'import React from "react";\nimport {{ use{stem}Controller }} from "./use{stem}Controller";\n'
                              f'import {{ HeaderPartial }} from "./partials/HeaderPartial";\n'
                              f'import {{ BodyPartial }} from "./partials/BodyPartial";\n\n'
                              f"export const {stem}: React.FC = () => {{\n"
                              f"  const ctrl = use{stem}Controller();\n"
                              f'  return (<div className="{stem.lower()}-container"><HeaderPartial /><BodyPartial /></div>);\n}};\n',
            ),
            SplitSubModule(
                file_name="partials/HeaderPartial.tsx",
                target_lines=max(50, min(120, total_lines // 4)),
                responsibility="Sous-vue visuelle de l'entête / barre d'actions",
                suggested_symbols=["HeaderPartial"],
                skeleton_code='import React from "react";\n\nexport const HeaderPartial: React.FC = () => <header></header>;\n',
            ),
            SplitSubModule(
                file_name="partials/BodyPartial.tsx",
                target_lines=max(70, min(160, total_lines // 3)),
                responsibility="Sous-vue visuelle principale ou formulaire atomique",
                suggested_symbols=["BodyPartial"],
                skeleton_code='import React from "react";\n\nexport const BodyPartial: React.FC = () => <main></main>;\n',
            ),
        ]

        barrel = (
            f'// Point d\'entrée unique du composant modulaire (Barrel Export)\n'
            f'export {{ {stem} }} from "./{stem}";\n'
            f'export {{ use{stem}Controller }} from "./use{stem}Controller";\n'
        )

        return SplitPlan(
            original_file=str(path).replace("\\", "/"),
            relative_path=path.name,
            total_lines=total_lines,
            language="react_tsx",
            pattern_type="REACT_PARTIALS",
            target_directory=comp_dir,
            sub_modules=sub_modules,
            barrel_export_skeleton=barrel,
            guidance_notes=[
                "Appliquer strictement l'Architecture en Puzzle (N2 Feature ou N3 Section).",
                "Ne pas mettre d'état (useState/useEffect) dans les partials visuels : passer les props depuis le contrôleur.",
                "L'orchestrateur principal doit faire moins de 100 lignes.",
            ],
        )


    def _generate_data_blueprint(self, path: Path, content: str, total_lines: int) -> SplitPlan:
        """Génère un plan de découpage pour un fichier de données / catalogue TypeScript/JS pur (sans JSX)."""
        stem = path.stem
        target_dir = str(path.parent / stem).replace("\\", "/")

        sub_modules = [
            SplitSubModule(
                file_name="types.ts",
                target_lines=max(40, min(120, total_lines // 5)),
                responsibility="Modèles de données, interfaces TypeScript et types union du catalogue",
                suggested_symbols=[f"{stem}Item", f"{stem}Category"],
                skeleton_code=f'export interface {stem}Item {{\n  id: string;\n  sku: string;\n  name: string;\n  price: number;\n  attributes?: Record<string, any>;\n}}\n',
            ),
            SplitSubModule(
                file_name="constants.ts",
                target_lines=max(30, min(80, total_lines // 6)),
                responsibility="Constantes, clés de filtrage, métadonnées et configurations",
                suggested_symbols=["DEFAULT_CATALOG_CONFIG", "CATEGORIES"],
                skeleton_code='export const DEFAULT_CATALOG_CONFIG = { active: true };\nexport const CATEGORIES = [] as const;\n',
            ),
            SplitSubModule(
                file_name="items_collection.ts",
                target_lines=max(80, min(220, total_lines // 2)),
                responsibility="Données atomiques scindées en sous-collections de taille raisonnable (< 250 lignes)",
                suggested_symbols=[f"{stem.lower()}_items"],
                skeleton_code=f'import {{ {stem}Item }} from "./types";\n\nexport const {stem.lower()}_items: {stem}Item[] = [];\n',
            ),
        ]

        barrel = (
            f"// Point d'entrée unique du catalogue modulaire (Barrel Export)\n"
            f'export * from "./types";\n'
            f'export * from "./constants";\n'
            f'export * from "./items_collection";\n'
        )

        return SplitPlan(
            original_file=str(path).replace("\\", "/"),
            relative_path=path.name,
            total_lines=total_lines,
            language="typescript_data",
            pattern_type="DATA_MODULES_SPLIT",
            target_directory=target_dir,
            sub_modules=sub_modules,
            barrel_export_skeleton=barrel,
            guidance_notes=[
                "Séparer les types et interfaces TypeScript dans 'types.ts'.",
                "Découper la collection de données volumineuse en sous-fichiers catégoriels de moins de 250 lignes.",
                "Conserver l'ancien fichier comme point d'entrée barrel export pour une compatibilité ascendante à 100%.",
            ],
        )

    def _generate_generic_blueprint(self, path: Path, content: str, total_lines: int) -> SplitPlan:
        """Génère un plan générique de découpage."""
        stem = path.stem
        subpkg = str(path.parent / f"{stem}_modules").replace("\\", "/")
        return SplitPlan(
            original_file=str(path).replace("\\", "/"),
            relative_path=path.name,
            total_lines=total_lines,
            language="generic",
            pattern_type="GENERIC_MODULAR",
            target_directory=subpkg,
            sub_modules=[
                SplitSubModule(
                    file_name="core.py",
                    target_lines=total_lines // 2,
                    responsibility="Cœur de traitement",
                    suggested_symbols=["CoreService"],
                    skeleton_code="# Logique centrale\n",
                ),
                SplitSubModule(
                    file_name="utils.py",
                    target_lines=total_lines // 2,
                    responsibility="Utilitaires et auxiliaires",
                    suggested_symbols=["helper"],
                    skeleton_code="# Utilitaires\n",
                ),
            ],
            barrel_export_skeleton="# Barrel export\n",
            guidance_notes=["Découper selon la responsabilité unique (SRP)."],
        )
