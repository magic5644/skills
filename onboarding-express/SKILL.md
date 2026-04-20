---
name: onboarding-express
description: 'Guided project tour for new developers using Graph-It-Live. Use when: onboarding a new developer, project overview, architecture tour, explain codebase, find entry points, find business logic, find most complex module, project walkthrough, new to the project, découvrir le projet, visite guidée, onboarding, point d''entrée, logique métier, module complexe.'
argument-hint: 'Which project or folder do you want to explore?'
---

# Onboarding Express

AI-guided architectural tour of any codebase for a new developer.
Powered by Graph-It-Live — extracts entry points, business logic, and the most complex module in one structured pass.

## Requires

Graph-It-Live CLI installed and indexed:

```bash
npm install -g @magic5644/graph-it-live
graph-it scan
```

## When to Use

- A developer joins the team and needs a codebase overview
- You want to understand an unfamiliar project quickly
- You need to identify where business logic lives before a refactor
- You want to find the most complex/risky module before making changes

---

## Workflow — Step by Step

### Step 1 — Build the index

```bash
graph-it scan
```

Always run first. All subsequent commands depend on it.

---

### Step 2 — Workspace overview

```bash
graph-it summary --format toon
```

Parse the output to identify:
- Top-level files and their role
- Candidate **entry point files** (look for: `index`, `main`, `app`, `server`, `cli`, `bootstrap`, `startup` in filenames or in exported symbols)
- Candidate **business logic folders** (look for: `services`, `domain`, `core`, `usecases`, `business`, `handlers`, `controllers`)

---

### Step 3 — Identify the 3 main entry points

For each candidate entry file (max 5), run:

```bash
graph-it explain <filePath> --format toon
```

Rank by:
1. **Highest fan-out** (the file that calls the most other files) → main orchestrators
2. **Top-level exports** that are referenced by many other files
3. Presence of bootstrap / initialization patterns in the call tree

Select the **top 3** and for each, produce:

> **Entry point `<filename>`** — `<one-line role description>`
> Called by: `<callers or "root — no callers (true entry point)">` 
> Calls into: `<top 3–5 downstream modules>`

---

### Step 4 — Locate the business logic

For each candidate business logic file, run:

```bash
graph-it tool generate_codemap --filePath=<absolutePath>
```

Look for files that:
- Export many symbols (functions, classes)
- Have deep internal call hierarchies
- Are imported by many other files (high fan-in)

Cross-check with:

```bash
graph-it tool find_referencing_files --filePath=<absolutePath>
```

Pick the **1–3 files** with the highest combination of fan-in + exported symbol count. These are the business logic core.

---

### Step 5 — Find the most complex module

For each file in the index (or a sampled top-20 by size), run:

```bash
graph-it tool analyze_file_logic --filePath=<absolutePath>
```

Score each file using this heuristic:

| Signal | Weight |
|---|---|
| Internal call depth (max recursion level) | High |
| Number of internal cycles (circular calls) | High |
| Number of exported symbols | Medium |
| Number of distinct callers (fan-in) | Medium |
| Number of distinct callees (fan-out) | Medium |

The file with the highest combined score is the **most complex module**.

---

### Step 6 — Trace the critical path

From the highest-scored entry point, trace the full execution chain:

```bash
graph-it trace <entryFile>#<mainFunction> --format mermaid
```

Render the Mermaid diagram to give the developer a visual of the critical path.

---

## Output Format

Synthesize steps 3–6 into this structured report:

---

### Project Tour — `<ProjectName>`

**3 Main Entry Points**

| # | File | Role | Type |
|---|------|------|------|
| 1 | `src/index.ts` | Application bootstrap, wires all modules | True entry (no callers) |
| 2 | `src/api/router.ts` | HTTP routing, dispatches to controllers | Called by index.ts |
| 3 | `src/cli.ts` | CLI interface, alternative entry point | True entry (no callers) |

**Business Logic Core**

| File | Exported Symbols | Referenced By |
|------|-----------------|---------------|
| `src/services/orderService.ts` | 12 | 8 files |
| `src/domain/pricing.ts` | 7 | 5 files |

**Most Complex Module**

> `src/services/orderService.ts` — 4 levels of internal call depth, 2 internal cycles, imported by 8 files.
> **Recommendation**: Any change here has high blast radius. Run `get_impact_analysis` before modifying.

**Critical Path (Mermaid)**

```mermaid
<trace output here>
```

---

## Tips

- On a **monorepo**, scope the tour per package: `graph-it scan --root packages/api` then repeat the workflow.
- If `graph-it summary` returns too much data, filter by folder: `graph-it summary src/core --format toon`.
- The "most complex module" heuristic is architectural, not cyclomatic. For line-level complexity, combine with a linter.
- After the tour, run Dead Code Hunter to find safe cleanup targets before the new developer starts writing code.
