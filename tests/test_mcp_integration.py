"""Tests d'intégration conformes au protocole officiel MCP et JSON-RPC 2.0."""
import json
import subprocess
import sys
from pathlib import Path
import pytest

_TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

from code_splitter_core.application.file_scanner import FileScannerService
from code_splitter_core.application.blueprint_generator import BlueprintGeneratorService


def test_threshold_exact_boundaries(tmp_path: Path):
    """Vérifie précisément les cas limites des seuils (250, 251, 350, 351 lignes)."""
    # 250 lignes -> CONFORME
    f250 = tmp_path / "f250.py"
    f250.write_text("\n".join(f"# line {i}" for i in range(250)), encoding="utf-8")

    # 251 lignes -> ALERTE (WARNING)
    f251 = tmp_path / "f251.py"
    f251.write_text("\n".join(f"# line {i}" for i in range(251)), encoding="utf-8")

    # 350 lignes -> ALERTE (WARNING)
    f350 = tmp_path / "f350.py"
    f350.write_text("\n".join(f"# line {i}" for i in range(350)), encoding="utf-8")

    # 351 lignes -> CRITIQUE (CRITICAL)
    f351 = tmp_path / "f351.py"
    f351.write_text("\n".join(f"# line {i}" for i in range(351)), encoding="utf-8")

    scanner = FileScannerService()
    report = scanner.audit_directory(tmp_path, warn_threshold=250, critical_threshold=350)

    assert report.total_files_scanned == 4
    assert report.conform_count == 1   # f250
    assert report.warn_count == 2      # f251 et f350
    assert report.critical_count == 1  # f351

    by_name = {Path(m.path).name: m.status for m in report.heavy_files}
    assert by_name["f251.py"] == "ALERTE"
    assert by_name["f350.py"] == "ALERTE"
    assert by_name["f351.py"] == "CRITIQUE"


def test_mcp_full_handshake_and_tool_call():
    """Vérifie le cycle de vie complet STDIO du protocole MCP officiel."""
    server_script = _TOOL_ROOT / "canal_mcp" / "mcp_server.py"

    proc = subprocess.Popen(
        [sys.executable, str(server_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    def send_and_recv(payload: dict) -> dict:
        line = json.dumps(payload) + "\n"
        proc.stdin.write(line)
        proc.stdin.flush()
        out_line = proc.stdout.readline()
        return json.loads(out_line)

    def send_notification(payload: dict):
        line = json.dumps(payload) + "\n"
        proc.stdin.write(line)
        proc.stdin.flush()

    try:
        # 1. Étape initialize
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        init_resp = send_and_recv(init_req)
        assert init_resp["id"] == 1
        assert "result" in init_resp
        assert init_resp["result"]["protocolVersion"] == "2024-11-05"
        assert init_resp["result"]["serverInfo"]["name"] == "mcp-10-code-splitter-auditor"

        # 2. Notification initialized (JSON-RPC 2.0 : aucune réponse autorisée)
        send_notification({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })

        # 3. Ping
        ping_resp = send_and_recv({"jsonrpc": "2.0", "id": 2, "method": "ping"})
        assert ping_resp["id"] == 2
        assert ping_resp["result"] == {}

        # 4. tools/list
        list_resp = send_and_recv({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
        assert list_resp["id"] == 3
        tools = list_resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        assert "audit_code_weight" in tool_names
        assert "generate_split_blueprint" in tool_names

        # 5. tools/call -> audit_code_weight
        call_resp = send_and_recv({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "audit_code_weight",
                "arguments": {"target_dir": str(_TOOL_ROOT / "canal_mcp")}
            }
        })
        assert call_resp["id"] == 4
        content_text = call_resp["result"]["content"][0]["text"]
        audit_data = json.loads(content_text)
        assert "total_files_scanned" in audit_data

        # 6. Méthode inconnue -> erreur -32601
        err_resp = send_and_recv({"jsonrpc": "2.0", "id": 5, "method": "unknown_proc"})
        assert err_resp["id"] == 5
        assert err_resp["error"]["code"] == -32601

    finally:
        proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=2)


def test_blueprint_typescript_real_symbol_extraction(tmp_path: Path):
    """Vérifie l'extraction des vrais symboles TypeScript dans le blueprint."""
    ts_file = tmp_path / "Catalog.ts"
    code = (
        "export interface ProductItem {\n"
        "  id: string;\n"
        "  title: string;\n"
        "  price: number;\n"
        "}\n\n"
        "export const CONFIG_SETTINGS = { active: true };\n"
        "export const ALL_PRODUCTS = [];\n"
    )
    ts_file.write_text(code, encoding="utf-8")

    generator = BlueprintGeneratorService()
    plan = generator.generate_plan(str(ts_file))

    assert plan.language == "typescript_data"
    assert plan.pattern_type == "DATA_MODULES_SPLIT"
    sub_map = {s.file_name: s for s in plan.sub_modules}
    assert "types.ts" in sub_map
    assert "ProductItem" in sub_map["types.ts"].suggested_symbols
    assert "CONFIG_SETTINGS" in sub_map["constants.ts"].suggested_symbols
    assert "ALL_PRODUCTS" in sub_map["items_collection.ts"].suggested_symbols
    assert "ProductItem" in plan.barrel_export_skeleton
