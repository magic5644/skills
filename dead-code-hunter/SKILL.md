---
name: dead-code-hunter
description: 'Scan the dependency graph for orphan nodes (uncalled symbols and unreferenced files) and propose safe, ranked deletions. Use when: dead code, unused code, orphan symbols, unreferenced files, cleanup, code hygiene, remove unused exports, find unused functions, find unused classes, supprimer code mort, code inutilisé, nettoyer le code, symboles non utilisés, exports inutiles.'
argument-hint: 'Which project, folder, or file do you want to scan for dead code?'
---

# Dead Code Hunter

Systematic scan of the dependency graph to surface orphan symbols and unreferenced files.
Produces a ranked, safety-annotated deletion plan powered by Graph-It-Live.

## Requires

Graph-It-Live CLI installed and indexed:

```bash
npm install -g @magic5644/graph-it-live
graph-it scan
```

## When to Use

- Before a major refactor — clean up before you restructure
- After removing a feature — confirm nothing is left dangling
- Periodic code hygiene pass on a growing codebase
- Before onboarding a new developer — reduce noise in the codebase

---

## Scope Caveat

> **`find_unused_symbols` operates per-file.** There is no single `graph-it deadcode --project` command (yet).
> This skill orchestrates multiple tool calls to achieve project-wide coverage.
> On very large projects (500+ files), prioritize high-risk folders (`src/`, `lib/`, `core/`) rather than scanning everything.
>
> For a fully automated single-pass solution, the right approach is a native `graph-it deadcode` CLI command
> built into `@magic5644/graph-it-live`. That would have significantly higher impact than this skill alone,
> but requires development work on the CLI itself.

---

## Workflow — Step by Step

### Step 1 — Build/refresh the index

```bash
graph-it scan
```

### Step 2 — Get the list of project files

```bash
graph-it tool get_index_status
```

Parse the output to retrieve the list of indexed source files. Filter out:
- `node_modules/`, `dist/`, `build/`, `.cache/`
- Test files (`*.test.*`, `*.spec.*`, `__tests__/`) — treat separately
- Type declaration files (`*.d.ts`)
- Configuration files (`*.config.*`, `vite.config.*`, etc.)

This is your **scan target list**.

---

### Step 3 — Per-file unused symbol scan

For each file in the scan target list, run:

```bash
graph-it tool find_unused_symbols --filePath=<absolutePath>
```

Collect results into a flat list:

```
[
  { file: "src/utils/format.ts", symbol: "formatCurrency", kind: "function" },
  { file: "src/services/legacyAuth.ts", symbol: "hashPasswordMD5", kind: "function" },
  ...
]
```

---

### Step 4 — Confirm with caller lookup (avoid false positives)

`find_unused_symbols` detects exports not imported by other files in the index.
However a symbol may be called **dynamically** or **from outside the indexed workspace** (e.g. a published library).
For every candidate, confirm with:

```bash
graph-it tool get_symbol_callers --filePath=<absolutePath> --symbolName=<symbol>
```

- **0 callers** → confirmed dead code candidate
- **1+ callers** → false positive, discard
- **Only test-file callers** → flag as "test-only symbol", handle separately

---

### Step 5 — Detect fully orphaned files

A file is a **ghost file** if:
1. It has 0 referencing files (nothing imports it)
2. It is not a known entry point (index, main, cli, server, etc.)

Check with:

```bash
graph-it tool find_referencing_files --filePath=<absolutePath>
```

A ghost file may contain multiple symbols — mark the entire file for deletion rather than symbol-by-symbol.

---

### Step 6 — Rank candidates by deletion safety

Apply this risk classification:

| Risk Level | Criteria | Action |
|---|---|---|
| **Safe** | 0 callers, 0 referencing files, not a public API export | Delete freely |
| **Likely safe** | 0 callers confirmed, file has other live symbols | Remove symbol, keep file |
| **Review first** | Symbol is exported from a barrel (`index.ts`) | Check if barrel is consumed externally |
| **Do not delete** | Dynamic call patterns detected (`eval`, string-based dispatch) | Flag only |
| **Test-only** | Only called from test files | Evaluate — may be intentional |

---

## Output Format

Produce a **Deletion Plan** in this format:

---

### Dead Code Scan Report

**Scanned**: `<N>` files | **Candidates found**: `<M>` symbols + `<K>` ghost files

#### Ghost Files (entire file can be deleted)

| File | Last modified | Reason |
|------|--------------|--------|
| `src/utils/oldMigration.ts` | 2022-03-11 | 0 imports, 0 callers, not an entry point |

**Suggested command:**
```bash
# Review first, then:
rm src/utils/oldMigration.ts
```

#### Orphan Symbols — Safe to Remove

| Symbol | File | Kind | Callers |
|--------|------|------|---------|
| `formatLegacyCurrency` | `src/utils/format.ts` | function | 0 |
| `MD5Hash` | `src/services/auth.ts` | function | 0 |

#### Orphan Symbols — Review First

| Symbol | File | Risk | Note |
|--------|------|------|------|
| `createReport` | `src/api/index.ts` | Barrel export | Check if consumed by external packages |

#### Test-Only Symbols

| Symbol | File | Test callers |
|--------|------|-------------|
| `mockPaymentGateway` | `src/mocks/payment.ts` | 3 test files |

---

### Recommended Deletion Order

1. Ghost files first — highest impact, no surgical precision needed
2. Orphan symbols in non-barrel files — safe, isolated changes
3. Barrel exports — requires checking external consumers
4. Test-only symbols — discuss with the team

---

## Safety Checklist Before Deleting

- [ ] Run `graph-it tool get_symbol_callers` one more time after any refactor that modified imports
- [ ] Check if the project is a **published library** — unused exports may be part of the public API
- [ ] Check `package.json` `exports` field — symbols exported via package entry points are always live
- [ ] Run the test suite after each deletion batch to catch dynamic usage not visible to static analysis
- [ ] Commit in small batches — one file or one symbol group per commit for easy revert

---

## Quick Scan (Single File or Folder)

If you only want to scan one file:

```bash
graph-it check src/utils/format.ts
graph-it tool find_unused_symbols --filePath=/abs/path/src/utils/format.ts
```

If you want a folder, use `graph-it summary <folder>` to get the file list, then iterate.

---

## Limitations & Future Improvements

- **Dynamic dispatch** (`obj[methodName]()`, `require(variable)`) is invisible to static analysis — always review before deleting
- **Monorepos**: scan per package, not at root, to avoid cross-package false positives
- **Framework magic**: decorators (`@Component`, `@Injectable`) may make symbols appear unused but they're resolved at runtime — exclude framework entry files from the scan
- **`graph-it deadcode` CLI command** (not yet available): a native single-pass project-wide dead code scanner would eliminate the per-file iteration overhead and provide a richer output with confidence scores. If this is a bottleneck, open an issue on `@magic5644/graph-it-live`.
