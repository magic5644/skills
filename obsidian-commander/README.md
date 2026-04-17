# Obsidian Commander

**Pilotez votre vault Obsidian depuis n'importe quel IDE ou CLI compatible avec les agents IA.**

Obsidian Commander est un **skill IA** complet qui permet de gérer toutes les fonctionnalités d'un vault Obsidian — création de notes, recherche sémantique, gestion du frontmatter, audit des liens, nettoyage, organisation, ingestion de contenu — directement depuis votre éditeur de code ou un terminal.

---

## Table des matières

- [Environnements supportés](#environnements-supportés)
- [Prérequis](#prérequis)
- [Installation](#installation)
  - [Installation automatique (tous les IDEs)](#installation-automatique-tous-les-ides)
  - [Installation manuelle par IDE](#installation-manuelle-par-ide)
  - [Installation en tant que skill de projet](#installation-en-tant-que-skill-de-projet)
- [Structure du projet](#structure-du-projet)
- [Guide d'utilisation](#guide-dutilisation)
  - [1. Créer des notes](#1-créer-des-notes)
  - [2. Rechercher dans le vault](#2-rechercher-dans-le-vault)
  - [3. Gérer le frontmatter (propriétés)](#3-gérer-le-frontmatter-propriétés)
  - [4. Auditer et mapper les liens](#4-auditer-et-mapper-les-liens)
  - [5. Nettoyer le vault](#5-nettoyer-le-vault)
  - [6. Organiser la structure du vault](#6-organiser-la-structure-du-vault)
  - [7. Ingérer du contenu externe](#7-ingérer-du-contenu-externe)
  - [8. Recherche sémantique (IA)](#8-recherche-sémantique-ia)
  - [9. Rapport de santé du vault](#9-rapport-de-santé-du-vault)
  - [10. Daily notes et tâches](#10-daily-notes-et-tâches)
  - [11. Plugins et thèmes (via CLI)](#11-plugins-et-thèmes-via-cli)
- [Utilisation avec les agents IA](#utilisation-avec-les-agents-ia)
  - [VS Code / GitHub Copilot](#vs-code--github-copilot)
  - [Claude Code / Claude CLI](#claude-code--claude-cli)
  - [Cursor](#cursor)
  - [Copilot CLI](#copilot-cli)
- [Référence des scripts](#référence-des-scripts)
- [Obsidian CLI](#obsidian-cli)
- [FAQ](#faq)

---

## Environnements supportés

| Environnement | Type | Chemin du skill |
| --- | --- | --- |
| **VS Code + GitHub Copilot** | IDE | `~/.copilot/skills/obsidian-commander/` |
| **Claude Code** | CLI | `~/.claude/skills/obsidian-commander/` |
| **Claude CLI** | CLI | `~/.claude/skills/obsidian-commander/` |
| **Cursor** | IDE | `~/.agents/skills/obsidian-commander/` |
| **Copilot CLI** | CLI | `~/.copilot/skills/obsidian-commander/` |
| **Autres agents compatibles** | IDE/CLI | `~/.agents/skills/obsidian-commander/` |
| **Projet spécifique** | Workspace | `.github/skills/obsidian-commander/` |

---

## Prérequis

### Obligatoire

- **Python 3.9+** (pour les scripts de gestion de vault)
- **Un vault Obsidian** (dossier contenant `.obsidian/`)

### Optionnel

- **Obsidian 1.12.7+** avec le CLI activé (pour les commandes `obsidian` en temps réel)
- **GPU** (accélère l'indexation sémantique, mais non requis — fonctionne sur CPU)

### Dépendances Python

```
sentence-transformers    # Modèle IA pour la recherche sémantique
faiss-cpu                # Index vectoriel rapide
numpy                    # Calcul numérique
pyyaml                   # Parsing YAML/frontmatter
tqdm                     # Barres de progression
beautifulsoup4           # Parsing HTML (pour l'ingestion)
markdownify              # Conversion HTML → Markdown
```

---

## Installation

### Installation automatique (tous les IDEs)

L'installeur copie le skill dans tous les emplacements compatibles en une seule commande.

**Windows (PowerShell) :**

```powershell
cd c:\github\obsidian-commander

# 1. Installer les dépendances Python
pip install -r requirements.txt

# 2. Installer le skill dans tous les IDEs
python scripts\install_skill.py --target all
```

**macOS / Linux :**

```bash
cd ~/github/obsidian-commander

# 1. Installer les dépendances Python
pip install -r requirements.txt

# 2. Installer le skill dans tous les IDEs
python scripts/install_skill.py --target all
```

Ou utiliser le script shell :

```bash
bash install.sh
```

### Installation manuelle par IDE

Si vous préférez n'installer que pour un seul environnement :

```bash
# VS Code / GitHub Copilot uniquement
python scripts/install_skill.py --target copilot

# Claude Code / Claude CLI uniquement
python scripts/install_skill.py --target claude

# Cursor / autres agents
python scripts/install_skill.py --target agents
```

### Installation en tant que skill de projet

Pour que le skill soit disponible uniquement dans un projet spécifique (partageable via Git) :

```bash
python scripts/install_skill.py --target project --project-dir /chemin/vers/votre/projet
```

Cela crée le dossier `.github/skills/obsidian-commander/` dans le projet cible.

---

## Structure du projet

```
obsidian-commander/
├── SKILL.md                        # ← Fichier principal lu par l'agent IA
├── README.md                       # ← Ce fichier
├── ai-instructions.md              # Instructions complémentaires pour l'IA
├── requirements.txt                # Dépendances Python
├── install.sh                      # Installeur bash (macOS/Linux)
├── install.ps1                     # Installeur PowerShell (Windows)
│
├── references/                     # Documentation de référence
│   ├── obsidian-cli.md             #   Commandes CLI Obsidian (40+ commandes)
│   └── obsidian-markdown.md        #   Syntaxe Obsidian (frontmatter, liens, tags)
│
├── scripts/                        # Scripts Python exécutables
│   ├── semantic_search.py          #   Recherche sémantique IA (FAISS)
│   ├── create_note.py              #   Création de notes avec templates
│   ├── link_audit.py               #   Audit complet des liens
│   ├── bulk_properties.py          #   Gestion en masse du frontmatter
│   ├── vault_cleanup.py            #   Nettoyage du vault
│   ├── vault_health.py             #   Rapport de santé
│   ├── scaffold_vault.py           #   Création de structure (PARA, Zettelkasten...)
│   ├── ingest.py                   #   Ingestion de contenu externe
│   └── install_skill.py            #   Installeur cross-IDE
│
└── src/
    └── engine.py                   # Moteur de recherche legacy (remplacé par scripts/)
```

---

## Guide d'utilisation

Chaque script peut être utilisé de **deux façons** :

1. **Via l'agent IA** : demandez en langage naturel dans le chat de votre IDE
2. **En ligne de commande** : exécutez directement les scripts Python

### 1. Créer des notes

#### Via l'agent IA

Dites simplement :

> "Crée une note Meeting dans mon vault Obsidian dans le dossier Projects"

> "Crée une note de type zettel sur le concept de Machine Learning"

#### En ligne de commande

```bash
# Note simple
python scripts/create_note.py --vault /chemin/vers/vault --name "Ma Note"

# Note avec template et tags
python scripts/create_note.py --vault . --name "Réunion Sprint 42" --template meeting --tags "meeting,sprint" --folder "Projects/Sprints"

# Note avec contenu et liens
python scripts/create_note.py --vault . --name "Concept IA" --template zettel --content "L'IA générative transforme..." --link-to "Machine Learning,Deep Learning"

# Lister les templates disponibles
python scripts/create_note.py --vault . --name x --list-templates
```

**Templates disponibles :**

| Template | Description | Tags par défaut |
| --- | --- | --- |
| `default` | Note standard avec frontmatter minimal | `[]` |
| `daily` | Note quotidienne | `[daily]` |
| `meeting` | Compte-rendu de réunion (agenda, notes, actions) | `[meeting]` |
| `project` | Fiche projet (overview, goals, tasks) | `[project]` |
| `zettel` | Note Zettelkasten (références, liens) | `[]` |
| `literature` | Note de lecture (summary, quotes, thoughts) | `[literature-note]` |

#### Via Obsidian CLI (si Obsidian est ouvert)

```bash
obsidian create name="Ma Note" content="# Ma Note\n\nContenu ici" open
obsidian create name="Sprint Review" template=Meeting
```

---

### 2. Rechercher dans le vault

#### Recherche textuelle (Obsidian CLI)

```bash
# Recherche simple
obsidian search query="architecture microservices"

# Recherche avec contexte (affiche les lignes autour du match)
obsidian search:context query="TODO" path="Projects/"

# Recherche par tag
obsidian search query="tag:#urgent"

# Recherche par propriété
obsidian search query="[status:draft]"
```

#### Recherche par propriétés (script)

```bash
# Trouver toutes les notes avec status=draft
python scripts/bulk_properties.py search --vault . --property status --value draft

# Trouver les notes sans frontmatter
python scripts/bulk_properties.py search --vault . --property tags

# Sortie JSON
python scripts/bulk_properties.py search --vault . --property status --value active --format json
```

#### Recherche sémantique IA

Voir [section dédiée](#8-recherche-sémantique-ia).

---

### 3. Gérer le frontmatter (propriétés)

Le frontmatter est le bloc YAML en haut de chaque note Obsidian :

```yaml
---
title: Ma Note
tags:
  - projet
  - actif
created: 2024-01-15
status: draft
---
```

#### Lecture

```bash
# Via CLI Obsidian
obsidian properties active                         # Propriétés du fichier actif
obsidian property:read name=tags file="Ma Note"    # Lire une propriété spécifique

# Via script
python scripts/bulk_properties.py search --vault . --property status
```

#### Modification unitaire (Obsidian CLI)

```bash
obsidian property:set name=status value=published file="Ma Note"
obsidian property:set name=tags value="[projet,terminé]" type=list
obsidian property:remove name=draft file="Ma Note"
```

#### Modification en masse (script)

```bash
# Passer toutes les notes taguées #draft en status=review
python scripts/bulk_properties.py update --vault . --filter "tag:#draft" --set "status=review"

# Ajouter archived=true à tout le dossier Archive/
python scripts/bulk_properties.py update --vault . --folder "Archive/" --set "archived=true"

# Renommer une propriété dans tout le vault
python scripts/bulk_properties.py update --vault . --rename "date:created"

# Supprimer une propriété de toutes les notes
python scripts/bulk_properties.py update --vault . --remove "obsolete_field"

# Mode dry-run (prévisualisation sans modification)
python scripts/bulk_properties.py update --vault . --filter "tag:#draft" --set "status=review" --dry-run
```

**Filtres disponibles :**

| Filtre | Exemple | Description |
| --- | --- | --- |
| `tag:#xxx` | `tag:#draft` | Notes ayant ce tag |
| `path:xxx` | `path:Projects/` | Notes dans ce dossier |
| `property:key=val` | `property:status=draft` | Propriété avec cette valeur |
| `missing:key` | `missing:created` | Notes sans cette propriété |
| Texte libre | `"TODO"` | Contenu contenant ce texte |

---

### 4. Auditer et mapper les liens

#### Commandes rapides (Obsidian CLI)

```bash
obsidian links file="Ma Note"       # Liens sortants
obsidian backlinks file="Ma Note"   # Liens entrants
obsidian unresolved                 # Liens cassés dans tout le vault
obsidian orphans                    # Notes sans liens entrants
obsidian deadends                   # Notes sans liens sortants
```

#### Audit complet (script)

```bash
# Rapport texte
python scripts/link_audit.py --vault /chemin/vers/vault

# Rapport JSON (pour traitement automatique)
python scripts/link_audit.py --vault . --format json
```

**Exemple de sortie :**

```
==================================================
       VAULT LINK HEALTH REPORT
==================================================
  Total notes:          342
  Total links:          1,205
  Resolved:             1,180 (97.9%)
  Unresolved:           25
  Orphan notes:         18
  Dead-end notes:       45
  Unique tags:          89
  No frontmatter:       12
==================================================

Unresolved links (25):
  [[API Reference]] — referenced from: Projects/Backend.md, Notes/Architecture.md
  [[Config Guide]] — referenced from: Setup/Install.md

Orphan notes (18):
  Archive/old-idea.md
  Notes/random-thought.md
```

---

### 5. Nettoyer le vault

#### Étape 1 : Générer un rapport (dry-run)

```bash
python scripts/vault_cleanup.py --vault . --action report
```

**Sortie :**

```
==================================================
       VAULT CLEANUP REPORT
==================================================
  Empty notes:               8
  Orphaned attachments:      15
  Duplicate tag variants:    3
  Notes without frontmatter: 12
==================================================

Empty notes (8):
  Notes/untitled.md
  Inbox/empty-idea.md
  ...

Orphaned attachments (15):
  Attachments/old-screenshot.png
  Attachments/diagram-v1.svg
  ...

Duplicate tag variants:
  project: ['project', 'Project']
  meeting: ['meeting', 'Meeting']
```

#### Étape 2 : Appliquer les corrections

```bash
# Corrections standard (ajoute le frontmatter manquant, supprime les notes vides)
python scripts/vault_cleanup.py --vault . --action fix

# Avec suppression des attachments orphelins (destructif !)
python scripts/vault_cleanup.py --vault . --action fix --fix-orphans
```

> **Attention :** `--fix-orphans` supprime des fichiers. Faites toujours un `--action report` d'abord et vérifiez la liste.

---

### 6. Organiser la structure du vault

#### Créer une structure depuis un template

```bash
# Voir les templates disponibles
python scripts/scaffold_vault.py --vault . --template zettelkasten --list

# Appliquer un template
python scripts/scaffold_vault.py --vault . --template para
```

**Templates d'organisation :**

| Template | Dossiers créés | Philosophie |
| --- | --- | --- |
| `zettelkasten` | Inbox, Fleeting, Literature, Permanent, MOC | Notes atomiques interconnectées |
| `para` | Projects, Areas, Resources, Archive | Méthode PARA de Tiago Forte |
| `gtd` | Inbox, Next Actions, Projects, Waiting For, Someday Maybe | Getting Things Done |
| `journal` | Daily Notes, Weekly Reviews, Monthly Reviews, Goals | Journal personnel |
| `research` | Papers, Literature Review, Experiments, Data, Drafts | Recherche académique |

Chaque template crée aussi un dossier `Templates/` avec des modèles de notes adaptés.

#### Déplacer et renommer (Obsidian CLI)

```bash
obsidian move file="Vieille Note" to="Archive/2024/"
obsidian rename file="Ancien Nom" name="Nouveau Nom"
```

---

### 7. Ingérer du contenu externe

Importez des fichiers externes dans votre vault.

#### Fichier unique

```bash
# Importer un fichier Markdown
python scripts/ingest.py --vault . file --source ~/Documents/notes.md

# Importer un fichier HTML (converti en Markdown)
python scripts/ingest.py --vault . file --source ~/Downloads/article.html --folder "Inbox" --tags "web,article"

# Importer un CSV (converti en tableau Markdown)
python scripts/ingest.py --vault . file --source data.csv --folder "Data"
```

#### Dossier entier

```bash
# Importer tous les fichiers .md et .txt d'un dossier
python scripts/ingest.py --vault . dir --source ~/old-notes/

# Importer uniquement les .html
python scripts/ingest.py --vault . dir --source ~/web-clips/ --ext ".html,.htm" --tags "web-clip"
```

#### Ajouter à la note du jour

```bash
python scripts/ingest.py --vault . daily --content "- [ ] Idée à explorer : agents autonomes"
```

**Formats supportés :** `.md`, `.txt`, `.html`, `.htm`, `.csv`, `.json`

---

### 8. Recherche sémantique (IA)

La recherche sémantique utilise un modèle d'IA (sentence-transformers) pour trouver des notes par **sens** plutôt que par mots-clés exacts.

#### Construire l'index

**Première utilisation** (indexe toutes les notes) :

```bash
python scripts/semantic_search.py --vault /chemin/vers/vault --action build
```

Durée : ~1-2 minutes pour 500 notes sur CPU. L'index est stocké dans `.obsidian/ai_index/`.

#### Mettre à jour l'index

Après avoir ajouté/modifié des notes :

```bash
python scripts/semantic_search.py --vault . --action update
```

#### Rechercher

```bash
# Recherche textuelle
python scripts/semantic_search.py --vault . --action ask --query "comment gérer les conflits en équipe"

# Plus de résultats
python scripts/semantic_search.py --vault . --action ask --query "machine learning" --top 20

# Sortie JSON
python scripts/semantic_search.py --vault . --action ask --query "productivité" --format json
```

**Exemple de sortie :**

```
Top 5 results for: "comment gérer les conflits en équipe"

  1. [[Communication Non Violente]] (Notes/CNV.md) — score: 0.823
  2. [[Gestion de Conflits]] (Projects/Management/Conflits.md) — score: 0.791
  3. [[Feedback Constructif]] (Areas/Leadership/Feedback.md) — score: 0.756
  4. [[Rétrospective Sprint 12]] (Projects/Sprints/Retro-12.md) — score: 0.698
  5. [[One on One Template]] (Templates/1on1.md) — score: 0.654
```

#### Choisir un modèle différent

```bash
# Modèle plus léger (plus rapide, moins précis)
python scripts/semantic_search.py --vault . --action build --model all-MiniLM-L6-v2

# Modèle multilingue (défaut, recommandé pour le français)
python scripts/semantic_search.py --vault . --action build --model paraphrase-multilingual-MiniLM-L12-v2
```

---

### 9. Rapport de santé du vault

```bash
# Rapport texte
python scripts/vault_health.py --vault /chemin/vers/vault

# Rapport JSON
python scripts/vault_health.py --vault . --format json
```

**Exemple de sortie :**

```
=======================================================
         OBSIDIAN VAULT HEALTH CHECK
=======================================================
  Vault:                  mon-vault
  Total size:             45.2 MB
  Notes:                  342
  Attachments:            128
  Total words:            185,430
  Avg words/note:         542
-------------------------------------------------------
  With frontmatter:       330
  Without frontmatter:    12
  Internal links:         1,205
  Embeds:                 89
  Unique tags:            67
  Unique properties:      15
-------------------------------------------------------
  Recently modified (7d): 23
  Stale (>90d):           45
=======================================================

Top Tags:
  #project: 89
  #meeting: 67
  #idea: 45
  #daily: 342
  #draft: 23

Largest Notes (by words):
  Projects/Architecture.md: 12,450 words
  Resources/API-Guide.md: 8,230 words
```

---

### 10. Daily notes et tâches

#### Via Obsidian CLI

```bash
# Ouvrir la note du jour
obsidian daily

# Lire le contenu
obsidian daily:read

# Ajouter une tâche
obsidian daily:append content="- [ ] Appeler le client"

# Ajouter du texte en haut de la note
obsidian daily:prepend content="## Objectif du jour\n\nFinaliser la proposition."

# Lister les tâches incomplètes du vault
obsidian tasks todo

# Lister les tâches de la note du jour
obsidian tasks daily

# Cocher une tâche
obsidian task ref="Daily Notes/2026-04-17.md:5" toggle
```

#### Via script (sans Obsidian)

```bash
python scripts/ingest.py --vault . daily --content "- [ ] Nouvelle tâche importante"
```

---

### 11. Plugins et thèmes (via CLI)

Nécessite Obsidian ouvert avec le CLI activé.

```bash
# Lister les plugins installés
obsidian plugins

# Installer et activer un plugin
obsidian plugin:install id=dataview enable

# Désactiver un plugin
obsidian plugin:disable id=daily-notes

# Recharger un plugin (développement)
obsidian plugin:reload id=mon-plugin

# Gérer les thèmes
obsidian themes
obsidian theme:set name="Minimal"
obsidian theme:install name="Catppuccin" enable

# Gérer les snippets CSS
obsidian snippets
obsidian snippet:enable name="custom-headers"
```

---

## Utilisation avec les agents IA

Le skill est conçu pour être **invoqué automatiquement** par l'agent IA quand vous posez des questions liées à Obsidian. Voici comment l'utiliser dans chaque environnement.

### VS Code / GitHub Copilot

1. Installez le skill : `python scripts/install_skill.py --target copilot`
2. Ouvrez le chat Copilot (`Ctrl+Shift+I`)
3. Tapez `/obsidian-commander` ou posez directement votre question :

**Exemples de prompts :**

```
Crée une note "Réunion Client" avec le template meeting dans mon vault ~/Documents/notes
Cherche sémantiquement "architecture hexagonale" dans mon vault
Fais un audit des liens de mon vault
Nettoie les notes vides et montre-moi le rapport d'abord
Scaffold mon vault avec la méthode PARA
Montre-moi la santé de mon vault
Quelles notes n'ont pas de frontmatter ?
Ajoute le tag #review à toutes les notes du dossier Draft/
```

### Claude Code / Claude CLI

1. Installez : `python scripts/install_skill.py --target claude`
2. Utilisez en CLI :

```bash
claude "Crée une note zettel sur le concept de Domain-Driven Design dans mon vault ~/vault"
claude "Fais un audit complet des liens de mon vault ~/notes"
```

### Cursor

1. Installez : `python scripts/install_skill.py --target agents`
2. Utilisez le chat Cursor avec les mêmes prompts que pour Copilot.

### Copilot CLI

```bash
gh copilot suggest "Cherche les notes orphelines dans mon vault Obsidian"
```

---

## Référence des scripts

| Script | Description | Commande rapide |
| --- | --- | --- |
| `semantic_search.py` | Recherche sémantique IA | `--action build\|update\|ask` |
| `create_note.py` | Créer des notes avec templates | `--name "X" --template meeting` |
| `link_audit.py` | Audit complet des liens | `--vault .` |
| `bulk_properties.py` | Gestion en masse du frontmatter | `update --set "k=v"` ou `search --property k` |
| `vault_cleanup.py` | Nettoyage du vault | `--action report\|fix` |
| `vault_health.py` | Rapport de santé | `--vault . --format text\|json` |
| `scaffold_vault.py` | Créer la structure du vault | `--template para\|zettelkasten\|gtd` |
| `ingest.py` | Importer du contenu externe | `file --source X` ou `dir --source X` |
| `install_skill.py` | Installer le skill | `--target all\|copilot\|claude\|agents` |

Tous les scripts acceptent `--help` pour la documentation complète :

```bash
python scripts/semantic_search.py --help
python scripts/create_note.py --help
```

---

## Obsidian CLI

Le skill s'intègre avec le **CLI officiel d'Obsidian** (1.12.7+). Voir la [référence complète](references/obsidian-cli.md) pour les 40+ commandes disponibles.

**Activer le CLI :**

1. Obsidian → Settings → General → Enable "Command line interface"
2. Redémarrer le terminal

**Commandes les plus utiles :**

```bash
obsidian vault                    # Info du vault
obsidian files                    # Lister les fichiers
obsidian search query="X"        # Rechercher
obsidian create name="X"         # Créer
obsidian read file=X              # Lire
obsidian daily                    # Note du jour
obsidian tasks todo               # Tâches en cours
obsidian tags counts              # Tags avec compteurs
obsidian backlinks file=X         # Liens entrants
obsidian eval code="..."          # Exécuter du JS
```

---

## FAQ

### Le skill ne se déclenche pas automatiquement

Vérifiez que le `SKILL.md` est bien dans le bon dossier :

```bash
# Vérifier l'installation
ls ~/.copilot/skills/obsidian-commander/SKILL.md    # Copilot
ls ~/.claude/skills/obsidian-commander/SKILL.md     # Claude
ls ~/.agents/skills/obsidian-commander/SKILL.md     # Agents
```

Le champ `description` du SKILL.md contient les mots-clés déclencheurs. Si l'agent ne le charge pas, essayez `/obsidian-commander` explicitement.

### Erreur "Not a valid Obsidian vault"

Le script cherche un dossier `.obsidian/` dans le chemin spécifié. Assurez-vous que :

- Le chemin pointe vers la **racine** du vault (pas un sous-dossier)
- Le vault a déjà été ouvert au moins une fois dans Obsidian

### La recherche sémantique est lente

- Le premier `build` télécharge le modèle (~500 MB). Les exécutions suivantes sont rapides.
- Utilisez `--action update` au lieu de `build` pour les mises à jour incrémentales.
- Sur un vault de 1000+ notes, comptez 2-3 minutes pour un build complet sur CPU.

### Comment utiliser avec un vault sur un NAS / cloud ?

Pointez simplement vers le chemin monté :

```bash
python scripts/vault_health.py --vault /mnt/nas/mon-vault
python scripts/semantic_search.py --vault "D:\OneDrive\Obsidian\mon-vault" --action build
```

### Les commandes `obsidian` ne fonctionnent pas

Le CLI Obsidian nécessite :

1. Obsidian **1.12.7+** installé
2. Le CLI activé dans Settings → General
3. L'application Obsidian **doit être ouverte**
4. Le terminal **redémarré** après l'activation

Si le CLI n'est pas disponible, tous les scripts Python fonctionnent de manière autonome sans Obsidian.

---

## Licence

MIT — Libre d'utilisation, de modification et de redistribution.
