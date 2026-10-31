---
name: mcp-10-code-splitter
description: Serveur MCP Code Splitter Auditor : Audit de budget de lignes (< 350L) et génération de plans de découpage modulaire.
---

# 🧬 SKILL ADN : MCP-10-CODE-SPLITTER
> **Classification :** Noyau Opérationnel Standardisé Snorbik AI (Directive Master V2.0)  
> **Mission :** Serveur MCP Code Splitter Auditor : Audit de budget de lignes (< 350L) et génération de plans de découpage modulaire.

---

## 1. Identité & Mission Critique

- **Nom officiel du Skill :** `mcp-10-code-splitter`
- **Rôle Fonctionnel :** Ce skill encapsule l'ADN technique, les règles de décision et les invariants opérationnels pour le sous-système `mcp-10-code-splitter`.
- **Déclencheur d'Activation :** Ce skill est activé dès qu'une IA ou un développeur intervient sur le périmètre correspondant ou traite des tâches de cette compétence.

---

## 2. Invariants Absolus & Interdictions (Vaccins)

Les règles suivantes sont formellement obligatoires et ne souffrent aucune dérogation :

- **INV-01 :** Règle #5 inviolable : Aucun fichier de code ne doit dépasser 350 lignes.
- **INV-02 :** Découpage systématique sous forme de package partials/ + index.ts barrel export.
- **INV-03 :** Zéro régression sur les imports externes après refactorisation.

---

## 3. Protocole d'Exécution Pas-à-Pas

Pour accomplir les missions de ce skill avec 100% de réussite :

1. Scanner l'arborescence avec mcp_scan_line_counts.
2. Pour chaque fichier > 300L, générer un plan de découpage modulaire (mcp_generate_split_plan).
3. Scaffolder le sous-répertoire partiel et ré-exporter les symboles publics.

---

## 4. Cartographie des Outils MCP & Scripts

Ce skill pilote et s'appuie sur les outils d'ingénierie suivants :

- `mcp_scan_line_counts`
- `mcp_generate_split_plan`

---

## 5. Résilience, Erreurs Fréquentes & Fallback

- Conserver une copie miroir du fichier d'origine jusqu'à validation complète de la suite de tests.

---

## 6. Procédure de Mutation (Enrichissement de l'ADN)

Raffinement des critères d'extraction sémantique (séparation hooks, types et sous-vues).

---
*Scellé et certifié conforme par la Gouvernance Génomique Snorbik AI © 2026.*
