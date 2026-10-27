# Graph-It Refactor

Safe refactoring for agentic coding workflows in three phases: map the impact read-only with Graph-It-Live, edit inside a sealed scope, then verify. No edit happens before a plan, and nothing is reported done before verification.

## What It Does

- Prefers the installed `graph-it` CLI; falls back to the MCP tools the host advertises, using their exact names and schemas.
- Phase 1 (read-only): `graph-it scan`, then one bounded call per target symbol: `graph-it context --mode refactor --depth 4 --detail compact --token-budget 4000 --format toon`. It returns importers (tests included), `indexRevision` and `truncated`; a truncated result continues with `--cursor`.
- Deepens only exported or widely used symbols with `get_impact_analysis` and `query_call_graph`; uses `verify_dependency_usage` when a file imports a module without clearly using the symbol.
- Follows re-exports: a barrel that only re-exports the symbol is expanded with `graph-it path-in <barrel>`, because impact, call-graph and `review-pr` consumers stop at the barrel.
- Records a baseline before moving or deleting code: `graph-it cycles <file>` and, when `graphit.architecture.json` exists, `graph-it check-architecture`.
- Presents a plan (files, importers, callers, tests, exports, cycles, gaps) before any edit.
- Phase 2: writes or updates the test for the changed behavior first, then edits only the planned files, keeping a compatibility re-export for a moved or renamed public symbol.
- Phase 3: `graph-it scan`, `graph-it review-pr --base HEAD`, `graph-it check-architecture`, then the project's formatter, typecheck, lint and the selected tests. A breaking change of severity `error` blocks even when `risk` is `low`.
- Stops and reports when required evidence is missing, partial (`isPartial`, `truncated`) or the index is stale.

## When to Use

Use it for refactors that touch several files or modules, change an exported signature, interface or package entry point, move or rename symbols, remove dead code, reorganize dependencies, or fix a complex regression.

Example prompts:

```text
Rename this exported function across the repo.
Move this class into a new services module and update callers.
Add a required parameter to this function and update everything it affects.
Remove this public interface and clean up dependencies safely.
```

## Requirements

- Graph-It-Live CLI **1.21.0 or later**. The skill checks `graph-it --version` once per session and uses only the commands listed by `graph-it --help` and `graph-it tool --list`.
- A terminal for the CLI, or a host that advertises the matching MCP tools.
- Native editing tools for Phase 2.

`graph-it update` is never run without explicit confirmation; silence, timeout, non-interactive execution and generic Agent mode are not consent.

## Limits

Static analysis does not prove behavior. The skill reports known gaps (dynamic dispatch, reflection, generated code, type-only references, public API surface, unsupported languages) and relies on tests to cover behavior.

## Related Skills

- [graph-it-live](../graph-it-live/) - dependency, call-graph and architecture questions
- [dead-code-hunter](../dead-code-hunter/) - ranked deletion plan for unused code
- [pr-review](../pr-review/) - review of the finished diff
