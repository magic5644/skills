# Dead Code Hunter

Scan your dependency graph for orphan symbols and ghost files, then get a ranked, safety-annotated deletion plan.
Powered by [Graph-It-Live](../graph-it-live/).

## What It Does

- Detects **exported symbols with 0 callers** across your project
- Identifies **ghost files** (files not imported anywhere, not an entry point)
- Confirms candidates via `get_symbol_callers` to eliminate false positives
- Classifies each candidate by **deletion safety** (Safe / Likely safe / Review first / Do not delete)
- Produces a **prioritized deletion plan** with ready-to-run commands

## Requirements

- [Graph-It-Live](https://www.npmjs.com/package/@magic5644/graph-it-live) CLI (`npm install -g @magic5644/graph-it-live`)
- Supported languages: TypeScript, JavaScript, Python, Rust, C#, Go, Java, Vue, Svelte

## Installation

```bash
npx skills add magic5644/skills/dead-code-hunter
```

## Usage

Trigger with natural language in your agent:

> "Find all dead code in this project"
> "Which functions are never called?"
> "Scan for orphan files"
> "Clean up unused exports in src/"

## Scan Scope

`graph-it check` scans the workspace in one pass; pass a file or folder to constrain the scope.
For agent integrations, use `scan_dead_code` with `scopePath`:

```bash
graph-it scan
graph-it check src/
graph-it tool scan_dead_code --scopePath=/absolute/path/to/project/src --format=toon
```

Confirm high-priority candidates individually with `get_symbol_callers` and
`find_referencing_files` before deleting them.

## Limitations

- Dynamic dispatch (`obj[method]()`, `require(variable)`) is invisible to static analysis
- Framework decorators (`@Component`, `@Injectable`) may produce false positives
- Published library exports may appear "unused" but are part of the public API

## Related Skills

- [graph-it-live](../graph-it-live/) — underlying dependency analysis engine
- [onboarding-express](../onboarding-express/) — use Dead Code Hunter before onboarding a new developer
- [pr-review](../pr-review/) — review cleanup diffs before merge
