---
name: graph-it-refactor
description: Use when refactoring multiple files, changing exported signatures or interfaces, moving symbols, deleting dead code, reorganizing dependencies, or fixing complex regressions.
---

# Graph-It Refactor

Safe two-phase refactoring for changes whose blast radius is larger than one local implementation detail.
Map semantic impact with Graph-It-Live before editing code with the host IDE's native tools.

## Valid Phase 1 Opening

When the target file and exported symbol are known, the first Graph-It-Live actions are this exact gate:

```text
1. graphitlive_generate_codemap({ filePath: "/abs/path/to/source.ext", format: "toon" })
2. graphitlive_get_impact_analysis({ filePath: "/abs/path/to/source.ext", symbolName: "ExportedSymbol", format: "toon" })
3. graphitlive_get_symbol_callers({ filePath: "/abs/path/to/source.ext", symbolName: "ExportedSymbol", format: "toon" })
4. graphitlive_crawl_dependency_graph({ filePath: "/abs/path/to/source.ext", format: "toon" })
5. Summarize source files, impacted callers/importers/exports, cycles, and analysis gaps before editing.
```

If the target file is unknown, first use read-only search or IDE navigation to resolve it. Then run the same gate.

## Canonical Graph-It-Live Tools

Use these exact MCP tool names. Do not invent aliases such as `find_symbol`, `find_references`, `impact_analysis`, `dependency_impact`, `validate_references`, or `refresh_index`.
Do not rewrite these names with prefixes or separators such as `mcp__graph_it_live__...`, `graph-it-live...`, `graph-it-live....`, or `graph_it_live...`.
Any refactor plan that names a Graph-It-Live analysis tool outside the four names below is invalid and must be rewritten before continuing.

- `graphitlive_generate_codemap`
- `graphitlive_get_impact_analysis`
- `graphitlive_get_symbol_callers`
- `graphitlive_crawl_dependency_graph`

## When to Use

- A refactor touches multiple files or modules.
- An exported function, class, method, type, interface, or package entry point changes name, location, signature, or visibility.
- Code is being moved between files, folders, packages, or layers.
- Dead code removal or dependency reorganization could affect callers, imports, or package exports.
- A complex regression may be caused by call graph, dependency, or module-boundary changes.

## Phase 1: Semantic Mapping and Impact Analysis

This phase is read-only. Do not call write-capable tools, formatters, codemods, package managers that mutate files, or shell commands that alter the worktree.
Read-only search commands may be used to locate target files, but they never replace Graph-It-Live evidence.

### Pre-Edit Evidence Gate

Before any edit, action plans and tool calls must name all required Graph-It-Live tools and include `format: "toon"` wherever the tool schema supports it:

| Evidence | Required tool call |
| --- | --- |
| Target structure | `graphitlive_generate_codemap` with the target file and `format: "toon"` |
| Exported-symbol blast radius | `graphitlive_get_impact_analysis` with target file, symbol name, and `format: "toon"` |
| Caller confirmation | `graphitlive_get_symbol_callers` with target file, symbol name, and `format: "toon"` |
| Dependency cycles and transitive module effects | `graphitlive_crawl_dependency_graph` with the touched entry file or module and `format: "toon"` |

If any required Graph-It-Live tool is unavailable, blocked, or returns partial evidence, stop before editing and report the gap. Do not replace the missing tool with text search.
Do not add extra Graph-It-Live discovery tools to this gate. Use read-only `rg` or IDE navigation only to resolve file paths needed by the four canonical tools.

Minimal planned-call shape:

```text
graphitlive_generate_codemap({ filePath: "/abs/path/to/source.ext", format: "toon" })
graphitlive_get_impact_analysis({ filePath: "/abs/path/to/source.ext", symbolName: "ExportedSymbol", format: "toon" })
graphitlive_get_symbol_callers({ filePath: "/abs/path/to/source.ext", symbolName: "ExportedSymbol", format: "toon" })
graphitlive_crawl_dependency_graph({ filePath: "/abs/path/to/source.ext", format: "toon" })
```

1. Generate a codemap for each target file with `graphitlive_generate_codemap`.
   The planned or executed call must explicitly include `format: "toon"` whenever the tool supports it.
2. For every exported symbol that may change, run `graphitlive_get_impact_analysis`.
   The planned or executed call must explicitly include `format: "toon"` whenever the tool supports it.
   Then run `graphitlive_get_symbol_callers` for the same exported symbol unless the tool is unavailable and that blocker is reported.
   Caller search with `rg`, IDE references, or tests is supporting evidence only; it does not satisfy this step.
3. Always run `graphitlive_crawl_dependency_graph` for the touched area to identify dependency cycles and transitive module effects.
   The planned or executed call must explicitly include `format: "toon"` whenever the tool supports it.
4. Before editing, present a concise action plan with:
   - source files to modify,
   - every caller, importer, dependent symbol, and package export that must be updated,
   - cycles, partial-analysis gaps, dynamic-dispatch risks, or public API compatibility risks.
   Omitting this plan means Phase 1 is incomplete.

## Phase 2: Targeted Editing and Propagation

Start only after Phase 1 is complete and the action plan exists.

1. Apply the primary refactor using native editing primitives such as `apply_patch`, `edit_file`, or the IDE's structured edit tools.
2. Update each impacted caller, importer, dependent file, and export surface recorded in Phase 1.
3. Keep the scope sealed: only modify files identified by the semantic impact analysis, plus tests or generated metadata needed to validate the change.
4. Re-run the relevant Graph-It-Live checks after editing when imports, exports, symbols, or module boundaries changed.
5. Run the smallest meaningful formatter, typecheck, and test commands for the impacted area.

## Strict Rules

| Rule | Requirement |
| --- | --- |
| TOON output | Spell out `format: "toon"` in every Graph-It-Live plan or call that supports it. |
| No blind editing | Do not edit before `graphitlive_get_impact_analysis` has run for each changed exported symbol. |
| Caller completeness | Treat missing caller/importer evidence as a blocker, not as permission to guess. |
| Sealed scope | Do not broaden the refactor beyond files and symbols identified during Phase 1. |
| Cycle awareness | Run dependency graph crawling before every move, deletion, signature change, or module reorganization. |

## Common Mistakes

- Running `rg` only and assuming text matches are a complete impact analysis.
- Treating impact analysis as optional because the change "looks obvious".
- Inventing Graph-It-Live tool names instead of using the canonical MCP tool names listed above.
- Forgetting `format: "toon"` on Graph-It-Live calls and wasting context on larger outputs.
- Writing an action list that says "run Graph-It-Live" without naming the specific tools and TOON format.
- Making dependency crawling conditional on whether earlier results look suspicious.
- Claiming a narrow diff removes the need for impact or cycle analysis.
- Moving a public symbol without checking package exports, barrel files, and compatibility re-exports.
- Editing first, then using Graph-It-Live to justify the diff afterward.

## Red Flags

- "This is urgent, just rename it."
- "The references are obvious."
- "Tests are already red, so impact analysis can wait."
- "No need for a full architecture pass."
- "I'll fix imports after the move."
- "The host uses fully qualified MCP names, so I'll rename the tools."

These all mean: stop, complete Phase 1, then edit.
