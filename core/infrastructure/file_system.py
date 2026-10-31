"""Passerelle de système de fichiers avec support des chemins longs et résilience UTF-8."""
from pathlib import Path
from typing import Optional, List, Tuple


class FileSystemGateway:
    """Gestionnaire d'accès au système de fichiers sécurisé."""

    @staticmethod
    def normalize_path(path_str: str) -> Path:
        """Normalise un chemin en gérant la syntaxe Windows si nécessaire."""
        p = Path(path_str).resolve()
        return p

    @staticmethod
    def read_text_safe(file_path: Path) -> Tuple[str, List[str]]:
        """Lit un fichier texte avec fallback d'encodage (utf-8, cp1252, latin-1).
        
        Retourne (contenu_complet, liste_de_lignes).
        """
        encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
        raw_bytes = file_path.read_bytes()
        
        for enc in encodings:
            try:
                content = raw_bytes.decode(enc)
                lines = content.splitlines()
                return content, lines
            except UnicodeDecodeError:
                continue
        
        # Fallback de secours en remplaçant les octets non décodables
        content = raw_bytes.decode("utf-8", errors="replace")
        return content, content.splitlines()

    @staticmethod
    def count_lines(file_path: Path) -> int:
        """Compte rapidement le nombre de lignes physiques d'un fichier."""
        try:
            _, lines = FileSystemGateway.read_text_safe(file_path)
            return len(lines)
        except Exception:
            return 0
