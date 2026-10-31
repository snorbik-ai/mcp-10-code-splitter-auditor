"""Serveur MCP officiel #10 — Code Splitter & Heavy File Auditor.
Protocole JSON-RPC 2.0 / stdio standard pour les IDEs et agents IA.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Inclusion du chemin racine de l'outil dans sys.path
_TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

from canal_sdk_cli.sdk import CodeSplitterSDK

sdk = CodeSplitterSDK()

TOOLS_METADATA = [
    {
        "name": "audit_code_weight",
        "description": (
            "[AUDITEUR POIDS DE CODE OBLIGATOIRE] Surveillance continue de la Règle d'Architecture n°5. "
            "DÉCLENCHEUR OBLIGATOIRE : 1) Dès qu'un fichier de code est modifié ou créé. "
            "2) Obligatoirement avant tout commit ou fin de tâche pour recenser les fichiers en alerte (>250 lignes) et critiques (>350 lignes). "
            "OPÉRATION : Scanne récursivement les lignes physiques sans consommation de tokens LLM. "
            "SORTIE : Rapport d'audit classé avec total scanné, conformes, alertes, critiques et liste des fichiers lourds."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_dir": {
                    "type": "string",
                    "description": "Chemin du répertoire à scanner (optionnel, répertoire courant par défaut)."
                },
                "warn_threshold": {
                    "type": "integer",
                    "description": "Seuil de lignes pour déclencher l'alerte (défaut : 250).",
                    "default": 250
                },
                "critical_threshold": {
                    "type": "integer",
                    "description": "Seuil de lignes pour déclencher le niveau critique (défaut : 350).",
                    "default": 350
                }
            }
        }
    },
    {
        "name": "generate_split_blueprint",
        "description": (
            "[GÉNÉRATEUR DE DÉCOUPAGE CLÉ EN MAIN] Assistant de refactorisation modulaire anti-fichiers lourds. "
            "DÉCLENCHEUR OBLIGATOIRE : Dès qu'un fichier dépasse 250/350 lignes ou qu'une demande de modularisation/refactorisation est formulée. "
            "OPÉRATION : Analyse l'AST et les symboles du fichier pour générer le plan exemplaire clé en main (React partials + useController ou sous-package Python avec façade barrel export). "
            "SORTIE : Plan de découpage complet avec arborescence cible, liste des sous-modules et squelettes de code prêts à copier."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Chemin absolu ou relatif vers le fichier de code à découper."
                }
            },
            "required": ["file_path"]
        }
    }
]


def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Achemine l'appel d'outil MCP vers le SDK correspondant."""
    if tool_name == "audit_code_weight":
        target_dir = arguments.get("target_dir")
        warn_th = arguments.get("warn_threshold", 250)
        crit_th = arguments.get("critical_threshold", 350)
        return sdk.audit_code_weight(target_dir=target_dir, warn_threshold=warn_th, critical_threshold=crit_th)

    elif tool_name == "generate_split_blueprint":
        file_path = arguments.get("file_path")
        if not file_path:
            raise ValueError("Le paramètre 'file_path' est obligatoire.")
        return sdk.generate_split_blueprint(file_path=file_path)

    else:
        raise ValueError(f"Outil MCP inconnu: {tool_name}")


def run_stdio_server():
    """Boucle principale JSON-RPC 2.0 sur stdin / stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")

            if method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_METADATA}}
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                result = handle_tool_call(name, args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
