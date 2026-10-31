# mcp-10-code-splitter-auditor

[![Pôle Stratégique](https://img.shields.io/badge/P%C3%B4le-05_POLE_ARCHITECTURE_CODE_CLEAN-blue.svg)](#)
[![Nature Commerciale](https://img.shields.io/badge/Nature-UTILITAIRE-orange.svg)](#)
[![Visibilité](https://img.shields.io/badge/Visibilit%C3%A9-PUBLIC-green.svg)](#)
[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture%20Ports%20%26%20Adapters-teal.svg)](#)
[![Budget Lignes](https://img.shields.io/badge/R%C3%A8gle%20%235-%3C%20350%20Lignes%20Garanti-blueviolet.svg)](#)

> **UTILITAIRE OPEN-SOURCE DE RIGUEUR**  
> Gardien de la Règle #5 : détecte les fichiers > 350 lignes et propose le plan de découpage modulaire en sous-répertoires partiels. Outil d'autorité technique.

---

## 1. Fiche d'Identité & Modèle Commercial

| Champ | Valeur Stratégique |
| :--- | :--- |
| **Composant** | `mcp-10-code-splitter-auditor` |
| **Pôle d'Appartenance** | **Pôle 5 : Outillage de Notoriété, Code Clean & Pattern MCP** |
| **Modèle Business** | **UTILITAIRE OPEN-SOURCE DE RIGUEUR** |
| **Stratégie de Visibilité** | **PUBLIC OPEN-SOURCE (MIT)** |
| **Potentiel Marché** | Gardien de la Règle #5 : détecte les fichiers > 350 lignes et propose le plan de découpage modulaire en sous-répertoires partiels. Outil d'autorité technique. |

---

## 2. Guide d'Installation 1-Clic (Développeur Humain)

```bash
git clone https://github.com/snorbik-ai/mcp-10-code-splitter-auditor.git
cd mcp-10-code-splitter-auditor
python install.py
```

Le script installe automatiquement les dépendances requises et résout les chemins de manière dynamique (**zéro chemin Windows absolu en dur**).

---

## 3. Configuration 1-Clic pour Agents IA (Cursor, Antigravity, Claude Code)

Ajoutez ce bloc à votre fichier `.mcp.json` ou `mcp_config.json` :

```json
{
  "mcpServers": {
    "mcp-10-code-splitter-auditor": {
      "command": "python",
      "args": ["canal_mcp/mcp_server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      },
      "type": "stdio"
    }
  }
}
```

---

## 4. Catalogue Sémantique des Outils (`tools`)

| Outil (`name`) | Rôle & Fonction | Déclencheur d'Action (Quand l'appeler ?) | Arguments requis | Sortie Observable |
| :--- | :--- | :--- | :--- | :--- |
| `mcp_audit_file_budgets` | Traque les fichiers trop denses et propose le plan de modularisation propre. | **Dès qu'un composant dépasse 250 lignes.** | `target_dir (str), max_lines (int)` | Bilan des fichiers hors budget |

---

## 5. Exemples Concrets de Prompts Utilisateur

Vous pouvez déclencher immédiatement ce composant en formulant ces requêtes dans votre IDE :

1. *« Vérifie si des composants du projet dépassent le seuil de 350 lignes. »*
2. *« Propose un plan de découpage en partials pour les fichiers complexes. »*
3. *« Certifie la conformité de notre code avec la Règle d'Architecture #5. »*

---

## 📜 Propriété & Licence
Composant officiel de l'écosystème **SNORBIK AI © 2026**.  
Tous droits réservés.
