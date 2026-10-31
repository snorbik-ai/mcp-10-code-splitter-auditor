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
            "Auditeur de budget de lignes de code. "
            "Scanne récursivement les fichiers sources (.py, .ts, .tsx, .js, .jsx) sans consommer de tokens LLM. "
            "Convention de classification : <= 250 lignes (CONFORME), 251 à 350 lignes (ALERTE / WARNING), "
            "> 350 lignes (CRITIQUE / CRITICAL). "
            "Retourne la liste ordonnée des fichiers lourds et les métriques de répartition."
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
            "Générateur de plan de découpage modulaire architectural (Blueprint). "
            "Analyse syntaxique des déclarations de symboles (classes, fonctions, interfaces TypeScript, constantes) "
            "pour proposer une architecture découpée respectant la séparation des responsabilités. "
            "Produit l'arborescence cible, les sous-modules avec les symboles réels extraits et le barrel export."
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
    """Boucle principale JSON-RPC 2.0 sur stdin / stdout conforme au protocole MCP officiel."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method", "")

            # Notification JSON-RPC (sans id ou méthode notifications/*) : AUCUNE réponse autorisée par le protocole
            if req_id is None or method.startswith("notifications/"):
                continue

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "mcp-10-code-splitter-auditor", "version": "1.0.0"}
                    }
                }
            elif method == "ping":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            elif method == "tools/list":
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
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except Exception as e:
            if req.get("id") is not None:
                err_resp = {"jsonrpc": "2.0", "id": req.get("id"), "error": {"code": -32603, "message": str(e)}}
                sys.stdout.write(json.dumps(err_resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
