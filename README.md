# mcp-10-code-splitter-auditor

[![Pôle Stratégique](https://img.shields.io/badge/P%C3%B4le-05_POLE_ARCHITECTURE_CODE_CLEAN-blue.svg)](#)
[![Nature](https://img.shields.io/badge/Nature-UTILITAIRE-orange.svg)](#)
[![Visibilité](https://img.shields.io/badge/Visibilit%C3%A9-PUBLIC-green.svg)](#)
[![Version](https://img.shields.io/badge/Version-1.0.0-purple.svg)](#)
[![Standard](https://img.shields.io/badge/Standard-V14.1%20Clean%20Architecture-teal.svg)](#)

> **UTILITAIRE OPEN-SOURCE DE RIGUEUR**  
> L'auditeur de budget de lignes qui traque les fichiers de plus de 350 lignes et génère des plans de découpage modulaires automatiques en sous-packages propres.

---

## 1. Carte d'Identité & Rôle Métier

| Champ Stratégique | Valeur Officielle |
| :--- | :--- |
| **Composant Officiel** | `mcp-10-code-splitter-auditor` |
| **Pôle d'Appartenance** | **Pôle 5 : L'Outillage de Notoriété, Code Clean & Pattern MCP** |
| **Modèle Business** | **UTILITAIRE OPEN-SOURCE DE RIGUEUR** |
| **Politique de Visibilité** | **PUBLIC OPEN-SOURCE (MIT)** |
| **Mission Principale** | L'auditeur de budget de lignes qui traque les fichiers de plus de 350 lignes et génère des plans de découpage modulaires automatiques en sous-packages propres. |
| **Architecture** | Clean Architecture Tri-Canal (STDIO / CLI / SDK In-Process) |

---

## 2. Guide d'Installation 1-Clic

### Option A : Installation Automatisée 1-Clic (Recommandée)
Exécutez simplement le script `install.py` à la racine du dépôt :

```bash
python install.py
```

Ce script effectue automatiquement :
1. La vérification de votre environnement Python (>= 3.10).
2. L'installation des dépendances requises en mode éditable (`pip install -e .` ou `npm install`).
3. La détection et l'injection automatique du serveur dans la configuration de Cursor (`%USERPROFILE%/.cursor/mcp.json`) sans écraser vos autres outils.

### Option B : Installation Manuelle Développeur
```bash
pip install -e .
```

---

## 3. Configuration Manuelle (Cursor, Antigravity, Claude Desktop)

Si vous préférez déclarer manuellement ce serveur dans votre fichier `.cursor/mcp.json` ou `mcp_config.json`, ajoutez le bloc suivant :

```json
{
  "mcpServers": {
    "mcp-10-code-splitter-auditor": {
      "command": "python",
      "args": ["canal_mcp/mcp_server.py"],
      "env": { "PYTHONIOENCODING": "utf-8" },
      "type": "stdio"
    }
  }
}
```

---

## 4. Catalogue Sémantique des Outils (`tools`)

Ce composant expose des outils déterministes prêts à être invoqués par un modèle de langage (LLM) :

| Nom de l'Outil (`tool`) | Rôle & Fonction Technique | Déclencheur d'Action (*Quand l'IA DOIT-ELLE l'appeler ?*) | Paramètres Requis | Sortie Retournée |
| :--- | :--- | :--- | :--- | :--- |
| `audit_code_weight` | Scanne récursivement les fichiers sources (`.ts`, `.tsx`, `.js`, `.py`) sans consommer de tokens LLM.<br>Convention configurable :<br>• `<= 250 lignes` : Conforme<br>• `251 à 350 lignes` : Alerte (Warning)<br>• `> 350 lignes` : Critique | **Lors de l'audit de qualité ou avant de clore une tâche de développement.** | `target_dir (str, optionnel, défaut: ".")`<br>`warn_threshold (int, défaut: 250)`<br>`critical_threshold (int, défaut: 350)` | JSON DTO : total fichiers scannés, répartition conformes/alertes/critiques, durée d'exécution et top des fichiers lourds. |
| `generate_split_blueprint` | Analyse syntaxique des déclarations et symboles (classes, fonctions, interfaces TypeScript, constantes) pour générer un plan de découpage modulaire exemplaire (React partials + Hook contrôleur ou modules de données avec barrel export). | **Dès qu'un fichier critique (> 350 lignes) est détecté.** | `file_path (str, requis)` | Plan d'architecture découpée (arborescence cible, symboles réels extraits, squelettes de code et barrel export). |

---

## 5. Performances & Périmètre Mesurés en Conditions Réelles

Mesuré sur le banc d'essai du dépôt e-commerce BatiHome (`frontend/src`) :
- **Périmètre du projet audité** : **434 fichiers totaux**
  - **76 fichiers** archivés sous `_archive` (exclus automatiquement par convention d'audit).
  - **358 fichiers sources actifs** audités (`.ts`, `.tsx`).
- **Temps de scan** : **6,2 s** au démarrage à froid, **~0,15 s** à chaud (moyenne de 5 scans répétés).
- **Génération du blueprint modulaire** : **~425 ms** (avec extraction des vraies interfaces et constantes).
- **Empreinte token LLM** : **0 token** (calcul déterministe local sans appel API externe).

---

## 6. Cycle de Vie Protocolaire MCP Standard

Le serveur stdio implémente l'intégralité du cycle de vie MCP officiel (JSON-RPC 2.0) :
- `initialize` (négociation des versions et des capacités `tools`).
- `notifications/initialized` (accepté silencieusement sans réponse conformément à la norme).
- `ping` (vérification de connectivité).
- `tools/list` et `tools/call` (exécution déterministe).

---

## 6. Exemples Concrets de Prompts Utilisateur

Voici 3 exemples réels de requêtes que vous pouvez poser directement dans le chat de Cursor ou Claude Code pour faire travailler cet outil :

1. *« Lance audit_code_weight sur frontend/src pour trouver tous les fichiers qui dépassent 350 lignes. »*
2. *« Génère un plan de découpage modulaire avec generate_split_blueprint pour RawGlassRailingCatalog.ts. »*
3. *« Vérifie que la Règle #5 de budget de lignes est respectée sur l'ensemble de mes composants. »*

---

## 🛡️ Propriété Intellectuelle & Sécurité
- **Éditeur :** SNORBIK AI © 2026.
- **Classification :** Conforme à la Directive Maîtresse V14.1 (Recettes d'architecture sanctuarisées dans le Pôle 06).
- **Zéro Régression :** Respect strict des budgets de lignes et des normes de sécurité.
