"""Tests unitaires pour l'Outil MCP #10 — Code Splitter & Heavy File Auditor."""
import sys
from pathlib import Path
import pytest

_TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

from core.domain.rules import DEFAULT_WARN_THRESHOLD, DEFAULT_CRITICAL_THRESHOLD
from core.application.file_scanner import FileScannerService
from core.application.blueprint_generator import BlueprintGeneratorService
from canal_sdk_cli.sdk import CodeSplitterSDK
from canal_mcp.mcp_server import handle_tool_call


def test_file_scanner_detection(tmp_path: Path):
    """Vérifie la détection et la classification correcte des lignes."""
    # Créer un fichier conforme (50 lignes)
    small_file = tmp_path / "small.py"
    small_file.write_text("\n".join(f"print({i})" for i in range(50)), encoding="utf-8")

    # Créer un fichier en alerte (260 lignes)
    warn_file = tmp_path / "warn.py"
    warn_file.write_text("\n".join(f"print({i})" for i in range(260)), encoding="utf-8")

    # Créer un fichier critique (380 lignes)
    crit_file = tmp_path / "crit.py"
    crit_file.write_text("\n".join(f"print({i})" for i in range(380)), encoding="utf-8")

    scanner = FileScannerService()
    report = scanner.audit_directory(tmp_path, warn_threshold=250, critical_threshold=350)

    assert report.total_files_scanned == 3
    assert report.conform_count == 1
    assert report.warn_count == 1
    assert report.critical_count == 1
    assert len(report.heavy_files) == 2
    assert report.heavy_files[0].status == "CRITIQUE"
    assert report.heavy_files[1].status == "ALERTE"


def test_blueprint_generator_python(tmp_path: Path):
    """Vérifie la génération d'un plan de découpage pour un module Python."""
    py_file = tmp_path / "large_service.py"
    code = (
        "class OrderModel:\n    pass\n\n"
        "class InvoiceModel:\n    pass\n\n"
        "def process_order():\n    pass\n\n"
        "def send_invoice():\n    pass\n\n"
    )
    py_file.write_text(code, encoding="utf-8")

    generator = BlueprintGeneratorService()
    plan = generator.generate_plan(str(py_file))

    assert plan.language == "python"
    assert plan.pattern_type == "PYTHON_SUBMODULES"
    assert len(plan.sub_modules) == 3
    assert "from .domain_models import *" in plan.barrel_export_skeleton


def test_blueprint_generator_react(tmp_path: Path):
    """Vérifie la génération d'un plan de découpage pour un composant React TSX."""
    tsx_file = tmp_path / "OrderConfigurator.tsx"
    code = "export const OrderConfigurator = () => { return <div>Config</div>; };\n"
    tsx_file.write_text(code, encoding="utf-8")

    generator = BlueprintGeneratorService()
    plan = generator.generate_plan(str(tsx_file))

    assert plan.language == "react_tsx"
    assert plan.pattern_type == "REACT_PARTIALS"
    assert any(m.file_name.startswith("use") for m in plan.sub_modules)
    assert any("partials" in m.file_name for m in plan.sub_modules)


def test_sdk_and_mcp_handler(tmp_path: Path):
    """Vérifie l'intégration du SDK et du routeur MCP."""
    test_file = tmp_path / "helper.py"
    test_file.write_text("def hello(): return 'world'\n", encoding="utf-8")

    sdk = CodeSplitterSDK()
    report = sdk.audit_code_weight(target_dir=str(tmp_path))
    assert report["total_files_scanned"] == 1

    bp = sdk.generate_split_blueprint(file_path=str(test_file))
    assert bp["language"] == "python"

    # Test via handle_tool_call (MCP)
    mcp_report = handle_tool_call("audit_code_weight", {"target_dir": str(tmp_path)})
    assert mcp_report["total_files_scanned"] == 1

    mcp_bp = handle_tool_call("generate_split_blueprint", {"file_path": str(test_file)})
    assert mcp_bp["original_file"] == str(test_file).replace("\\", "/")
