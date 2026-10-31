"""Interface CLI terminal pour le Code Splitter & Heavy File Auditor."""
import argparse
import json
import sys
from pathlib import Path

# Inclusion de la racine de l'outil dans sys.path
_TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

from canal_sdk_cli.sdk import CodeSplitterSDK


def main():
    parser = argparse.ArgumentParser(
        description="Outil Interne #10 — Code Splitter & Heavy File Auditor"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Commande audit
    audit_parser = subparsers.add_parser("audit", help="Auditer le poids des fichiers de code")
    audit_parser.add_argument("--dir", default=".", help="Répertoire à auditer (défaut: .)")
    audit_parser.add_argument("--warn", type=int, default=250, help="Seuil d'alerte (défaut: 250)")
    audit_parser.add_argument("--critical", type=int, default=350, help="Seuil critique (défaut: 350)")
    audit_parser.add_argument("--json", action="store_true", help="Sortie en format JSON brut")

    # Commande blueprint
    bp_parser = subparsers.add_parser("blueprint", help="Générer un plan de découpage pour un fichier")
    bp_parser.add_argument("--file", required=True, help="Chemin du fichier à découper")
    bp_parser.add_argument("--json", action="store_true", help="Sortie en format JSON brut")

    args = parser.parse_args()
    sdk = CodeSplitterSDK()

    if args.command == "audit":
        report = sdk.audit_code_weight(
            target_dir=args.dir,
            warn_threshold=args.warn,
            critical_threshold=args.critical,
        )
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return

        print("=" * 80)
        print("📊 RAPPORT D'AUDIT DU POIDS DE CODE (Règle d'Architecture n°5)")
        print("=" * 80)
        print(f"  • Fichiers scannés : {report['total_files_scanned']}")
        print(f"  • Conformes (<= {args.warn} l.)  : {report['conform_count']}")
        print(f"  • En Alerte (> {args.warn} l.)   : {report['warn_count']}")
        print(f"  • Critiques (> {args.critical} l.)  : {report['critical_count']}")
        print(f"  • Temps d'exécution : {report['execution_ms']} ms")
        print("-" * 80)

        if report["heavy_files"]:
            print(f"{'Statut':10} | {'Lignes':7} | Fichier")
            print("-" * 80)
            for f in report["heavy_files"][:30]:  # Top 30
                status_icon = "🚨 CRITIQUE" if f["status"] == "CRITIQUE" else "⚠️ ALERTE  "
                print(f"{status_icon:10} | {f['line_count']:7} | {f['relative_path']}")
            if len(report["heavy_files"]) > 30:
                print(f"... et {len(report['heavy_files']) - 30} autres fichiers.")
        else:
            print("✅ Aucun fichier lourd détecté ! Tout est parfaitement conforme.")
        print("=" * 80)

    elif args.command == "blueprint":
        plan = sdk.generate_split_blueprint(args.file)
        if args.json:
            print(json.dumps(plan, indent=2, ensure_ascii=False))
            return

        print("=" * 80)
        print("🧩 PLAN DE DÉCOUPAGE MODULAIRE EXEMPLAIRE (BLUEPRINT)")
        print("=" * 80)
        print(f"  • Fichier Source  : {plan['original_file']}")
        print(f"  • Volume Actuel   : {plan['total_lines']} lignes")
        print(f"  • Patron Cible    : {plan['pattern_type']}")
        print(f"  • Dossier Cible   : {plan['target_directory']}")
        print("-" * 80)
        print("Sous-modules recommandés :")
        for sub in plan["sub_modules"]:
            print(f"  👉 {sub['file_name']:30} (~{sub['target_lines']} l.) : {sub['responsibility']}")
        print("-" * 80)
        print("Notes d'ingénierie :")
        for note in plan["guidance_notes"]:
            print(f"  • {note}")
        print("=" * 80)


if __name__ == "__main__":
    main()
