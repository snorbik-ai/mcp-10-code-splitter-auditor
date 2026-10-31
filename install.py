#!/usr/bin/env python3
"""
Script d'Installation Multi-Clients Universel & Injection MCP (v22.2)
Support Certifié :
- Cursor : ~/.cursor/mcp.json (clé "mcpServers")
- VS Code : .vscode/mcp.json (clé officielle "servers" selon spécification officielle)
- Claude Desktop : claude_desktop_config.json (clé "mcpServers")
- Claude Code CLI : exécution directe 'claude mcp add' avec fallback commande
Snorbik AI Architecture V22.2
"""
import sys
from snorbik_bootstrap import get_guaranteed_python
PYTHON_BIN = get_guaranteed_python()
import os
import json
import argparse
import platform
import shutil
import subprocess
from pathlib import Path

MIN_PYTHON = (3, 10)
COMPONENT_NAME = "mcp-10-code-splitter-auditor"
IS_NODE = False
ENTRYPOINT_REL = "canal_mcp/mcp_server.py"

def check_python_version():
    if sys.version_info < MIN_PYTHON:
        sys.stderr.write(f"[-] Erreur : Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ requis. Version actuelle : {sys.version}\n")
        sys.exit(1)
    print(f"[+] Python {sys.version.split()[0]} validé (OK).")

def install_dependencies(root_dir: Path):
    print(f"[*] Installation des dépendances pour {COMPONENT_NAME}...")
    if IS_NODE:
        if (root_dir / "package.json").exists():
            res = subprocess.run(["npm", "install"], cwd=str(root_dir), shell=True)
            if res.returncode != 0:
                sys.stderr.write(f"[-] Erreur critique : npm install a échoué (code {res.returncode}).\n")
                sys.exit(res.returncode)
    else:
        res = None
        if (root_dir / "pyproject.toml").exists() or (root_dir / "setup.py").exists():
            res = subprocess.run([str(PYTHON_BIN), "-m", "pip", "install", "-e", "."], cwd=str(root_dir), shell=True, capture_output=True, text=True)
        elif (root_dir / "requirements.txt").exists():
            res = subprocess.run([str(PYTHON_BIN), "-m", "pip", "install", "-r", "requirements.txt"], cwd=str(root_dir), shell=True, capture_output=True, text=True)
        
        if res is not None and res.returncode != 0:
            err_output = res.stderr.strip() if res.stderr else "Échec d'installation pip."
            sys.stderr.write(f"[-] Erreur critique : pip install a échoué (code {res.returncode}) :\n{err_output}\n")
            sys.exit(res.returncode)
    print(f"[+] Dépendances opérationnelles.")

def get_server_entry(entrypoint_full: Path) -> dict:
    if IS_NODE:
        return {
            "command": "node",
            "args": [str(entrypoint_full.as_posix())],
            "type": "stdio"
        }
    return {
        "command": str(PYTHON_BIN) if str(PYTHON_BIN) else "python",
        "args": [str(entrypoint_full.as_posix())],
        "env": {"PYTHONIOENCODING": "utf-8"},
        "type": "stdio"
    }

def configure_cursor(server_entry: dict, custom_home: Path = None) -> bool:
    cursor_dir = (custom_home or Path.home()) / ".cursor"
    cursor_config = cursor_dir / "mcp.json"
    return _inject_config(cursor_config, "mcpServers", COMPONENT_NAME, server_entry, "Cursor")

def configure_vscode(server_entry: dict, target_root: Path = None) -> bool:
    """
    Configure VS Code selon la spécification officielle :
    Fichier : .vscode/mcp.json
    Clé racine obligatoire : 'servers' (https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
    """
    vscode_dir = (target_root or Path.cwd()) / ".vscode"
    vscode_config = vscode_dir / "mcp.json"
    entry_vscode = {k: v for k, v in server_entry.items() if k != "type"}
    return _inject_config(vscode_config, "servers", COMPONENT_NAME, entry_vscode, "VS Code (clé: servers)")

def configure_claude_desktop(server_entry: dict, custom_appdata: Path = None) -> bool:
    if custom_appdata:
        claude_dir = custom_appdata / "Claude"
    else:
        system = platform.system()
        if system == "Windows":
            app_data = os.environ.get("APPDATA")
            if not app_data:
                return False
            claude_dir = Path(app_data) / "Claude"
        elif system == "Darwin":
            claude_dir = Path.home() / "Library" / "Application Support" / "Claude"
        else:
            claude_dir = Path.home() / ".config" / "Claude"
    
    claude_config = claude_dir / "claude_desktop_config.json"
    entry_claude = {k: v for k, v in server_entry.items() if k != "type"}
    return _inject_config(claude_config, "mcpServers", COMPONENT_NAME, entry_claude, "Claude Desktop", create_parents=False)

def configure_claude_code_cli(entrypoint_full: Path) -> bool:
    """Tente une injection directe via CLI claude si présent, sinon affiche la commande."""
    claude_bin = shutil.which("claude")
    cmd_args = ["claude", "mcp", "add", COMPONENT_NAME, str(PYTHON_BIN), str(entrypoint_full.as_posix())]
    if claude_bin:
        try:
            res = subprocess.run(cmd_args, capture_output=True, text=True, check=False)
            if res.returncode == 0:
                print(f"[+] Enregistré automatiquement dans Claude Code CLI via 'claude mcp add'.")
                return True
        except Exception:
            pass
    cmd_str = f'claude mcp add {COMPONENT_NAME} "{PYTHON_BIN}" "{entrypoint_full.as_posix()}"'
    print(f"[*] Commande Claude Code CLI :\n    {cmd_str}")
    return True

def _inject_config(file_path: Path, root_key: str, server_name: str, entry: dict, client_name: str, create_parents=True) -> bool:
    try:
        if create_parents:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        elif not file_path.parent.exists():
            return False
        
        data = {root_key: {}}
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8").strip()
            if content:
                try:
                    data = json.loads(content)
                except json.JSONDecodeError as err:
                    backup_path = file_path.with_suffix(file_path.suffix + ".corrupted.bak")
                    try:
                        shutil.copy2(file_path, backup_path)
                        backup_note = f"Sauvegarde de sécurité créée : {backup_path}"
                    except Exception:
                        backup_note = "Impossible de créer la sauvegarde."
                    sys.stderr.write(
                        f"[-] ERREUR CRITIQUE {client_name} : Le fichier {file_path} contient un JSON invalide ({err}).\n"
                        f"    Pour éviter toute perte de configuration, l'installateur refuse d'écraser ce fichier.\n"
                        f"    {backup_note}\n"
                        f"    Veuillez corriger la syntaxe JSON avant de relancer l'installation.\n"
                    )
                    return False
            if not isinstance(data, dict):
                sys.stderr.write(f"[-] ERREUR {client_name} : Le format JSON racine de {file_path} n'est pas un objet.\n")
                return False
            if root_key not in data:
                data[root_key] = {}
        
        data[root_key][server_name] = entry
        file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[+] Injecté dans {client_name} : {file_path}")
        return True
    except Exception as e:
        sys.stderr.write(f"[-] Avertissement injection {client_name} : {e}\n")
        return False

def main():
    parser = argparse.ArgumentParser(description=f"Installateur Multi-Clients {COMPONENT_NAME}")
    parser.add_argument("--client", choices=["all", "cursor", "vscode", "claude"], default="all",
                        help="Client cible (défaut : all pour auto-détection)")
    args = parser.parse_args()

    print("=" * 70)
    print(f"INSTALLATEUR MULTI-CLIENTS : {COMPONENT_NAME} (v22.2)")
    print("=" * 70)

    root_dir = Path(__file__).resolve().parent
    check_python_version()
    install_dependencies(root_dir)

    entrypoint_full = (root_dir / ENTRYPOINT_REL).resolve()
    server_entry = get_server_entry(entrypoint_full)

    results = []
    if args.client in ("all", "cursor"):
        ok = configure_cursor(server_entry)
        results.append(("Cursor", ok))
    if args.client in ("all", "vscode"):
        ok = configure_vscode(server_entry, root_dir)
        results.append(("VS Code", ok))
    if args.client in ("all", "claude"):
        ok_d = configure_claude_desktop(server_entry)
        ok_c = configure_claude_code_cli(entrypoint_full)
        results.append(("Claude Desktop / CLI", ok_d or ok_c))

    print("=" * 70)
    failed = [name for name, status in results if not status]
    if args.client != "all" and failed:
        sys.stderr.write(f"[-] Échec de configuration pour : {', '.join(failed)}\n")
        sys.exit(1)

    print(f"✅ Serveur MCP {COMPONENT_NAME} configuré avec succès !")
    print("💡 RAPPEL DX : Rechargez votre IDE ('Developer: Reload Window') pour l'activer.")
    print("=" * 70)

if __name__ == "__main__":
    main()
