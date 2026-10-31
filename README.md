# mcp-10-code-splitter-auditor

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](#)
[![Protocol](https://img.shields.io/badge/MCP_Protocol-2025--11--25-blue.svg)](#)
[![Architecture](https://img.shields.io/badge/Architecture-Hybride_Tri--Canal-teal.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)
[![Tests](https://img.shields.io/badge/Tests-7%2F7%20passed-brightgreen.svg)](#)
[![Status](https://img.shields.io/badge/Status-Active_Utility-blue.svg)](#)

> **Auditeur & Générateur de Blueprints Modulaires pour LLM & Coding Agents**  
> Traque les fichiers dépassant le budget de lignes (seuil d'alerte > 250, critique > 350 lignes) et génère des plans de découpage modulaire structurés (blueprints d'architecture sans altération destructive de code).

---

## 1. Carte d'Identité & Rôle Métier

| Propriété | Description |
| :--- | :--- |
| **Composant Officiel** | `mcp-10-code-splitter-auditor` |
| **Licence** | **MIT Open-Source** (usage commercial et personnel libre) |
| **Environnement** | Python 3.10+ (Windows, macOS, Linux) |
| **Clients Supportés & Testés** | **Cursor**, **VS Code**, **Claude Desktop**, **Claude Code CLI** |
| **Architecture** | **Clean Architecture Tri-Canal (STDIO / CLI / SDK In-Process)** |
| **Spécification MCP** | **JSON-RPC 2.0 (Cycle officiel 2025-11-25)** |

---

## 2. Guide d'Installation Multi-Clients

### Option A : Install with your AI Coding Agent (Recommandée)
Copiez-collez ce prompt prêt à l'emploi dans votre agent IA (Cursor Agent, Claude Code, VS Code Copilot) :

```text
Tu es mon ingénieur d'intégration. Configure le serveur MCP depuis ce dépôt :
1. Identifie le client MCP réellement actif dans notre session (Cursor, VS Code, Claude Code ou Claude Desktop).
2. Lis les instructions du README et sélectionne l'argument approprié pour l'installation (--client cursor, --client vscode, --client claude ou --client all).
3. Lance `python install.py --client <client_choisi>` et vérifie le code retour d'exécution.
4. Si nécessaire, rappelle-moi de recharger la fenêtre de mon client (Developer: Reload Window).
5. Vérifie que le serveur répond correctement en appelant l'outil `audit_code_weight` et confirme-moi le résultat du scan.
6. Rapporte-moi clairement le résultat du test et signale toute erreur éventuelle sans la masquer.
```

---

### Option B : Installation Automatisée 1-Clic (Terminal)
Exécutez simplement le script `install.py` à la racine du dépôt :

```bash
# Installation automatique tous clients détectés :
python install.py

# Ou installation ciblée selon votre environnement :
python install.py --client cursor   # Configure ~/.cursor/mcp.json (clé "mcpServers")
python install.py --client vscode   # Configure .vscode/mcp.json (clé officielle "servers")
python install.py --client claude   # Configure Claude Desktop et enregistre via claude mcp add
python install.py --client all      # Auto-détection et configuration universelle
```

#### Sécurité et Résilience de l'Installateur :
- **Vérification stricte de `pip install`** : toute anomalie de dépendances bloque l'installation avec code d'erreur explicite.
- **Protection anti-corruption JSON** : si un fichier de configuration existant est syntaxiquement invalide, l'installateur génère une copie de sauvegarde `.corrupted.bak` et **refuse formellement d'écraser le fichier**.
- **Préservation intégrale** : tous vos serveurs MCP et configurations existantes sont conservés sans perte.

---

### Option C : Installation Manuelle Développeur
```bash
# 1. Cloner et installer en mode éditable
git clone https://github.com/snorbik-ai/mcp-10-code-splitter-auditor.git
cd mcp-10-code-splitter-auditor
pip install -e .

# 2. Exécuter la suite de tests unitaires
pytest
```

---

## 3. Configuration Manuelle des Clients

Si vous préférez déclarer manuellement ce serveur dans votre configuration :

#### Pour Cursor (`~/.cursor/mcp.json`) & Claude Desktop (`claude_desktop_config.json`) :
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

#### Pour VS Code (`.vscode/mcp.json` - Spécification Officielle VS Code) :
```json
{
  "servers": {
    "mcp-10-code-splitter-auditor": {
      "command": "python",
      "args": ["canal_mcp/mcp_server.py"],
      "env": { "PYTHONIOENCODING": "utf-8" }
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
| `generate_split_blueprint` | Extraction ciblée des déclarations TypeScript / JavaScript / Python (`interface`, `type`, `const`, `function`, `class`) pour construire un blueprint de refactorisation propre (découpage modulaire proposé en partials et barrel exports, sans modification directe destructive des fichiers). | **Dès qu'un fichier critique (> 350 lignes) est détecté.** | `file_path (str, requis)` | Plan d'architecture découpée (arborescence cible, symboles réels extraits, squelettes de code et barrel export). |

---

## 5. Performances Mesurées en Conditions Réelles

Mesuré sur banc d'essai local (environnement Windows 11 / Python 3.12) :
- **Audit de lignes (`audit_code_weight`)** : **~117 ms** pour analyser ~350 fichiers sources (parcours local du système de fichiers).
- **Génération de blueprint (`generate_split_blueprint`)** : **~11 ms** à chaud en mémoire vive (~425 ms lors du premier appel à froid avec chargement initial des modules).
- **Empreinte token LLM** : **0 token** (calcul déterministe local sans appel API externe).
- **Suite de tests unitaires (`pytest`)** : **7/7 tests passés à 100%** en **0,90 s**.

---

## 6. Cycle de Vie Protocolaire MCP Standard

Le serveur stdio implémente l'intégralité du cycle de vie MCP officiel (JSON-RPC 2.0) :
- Handshake `initialize` (négociation des versions et des capacités `tools`).
- Réception silencieuse de `notifications/initialized` (accepté sans émission de réponse parasite).
- Requête `ping` (vérification de connectivité).
- Découverte et invocation d'outils `tools/list` et `tools/call`.

---

## 7. Exemples Concrets de Prompts Utilisateur

Voici 3 exemples réels de requêtes que vous pouvez poser directement dans le chat de Cursor ou Claude Code pour faire travailler cet outil :

1. *« Lance audit_code_weight sur mon dossier src pour identifier les fichiers dépassant 350 lignes. »*
2. *« Génère un blueprint de découpage modulaire avec generate_split_blueprint pour mon composant volumineux. »*
3. *« Vérifie que le budget maximal de 350 lignes par fichier est respecté sur l'ensemble de mon code source. »*

---

## 🛡️ Licence & Contribution
- **Éditeur :** SNORBIK AI © 2026.
- **Licence :** Open-Source sous licence MIT (libre pour projets commerciaux et open-source).
- **Spécification :** Conforme aux standards officiels MCP (Model Context Protocol).
- **Statut Public :** Certifié conforme V25 (Zéro référence interne, benchmarks locaux validés).
