# Graph-It Refactor

Safe two-phase refactoring for agentic coding workflows. This skill forces semantic impact mapping with Graph-It-Live before code is edited.

## What It Does

- Maps the target file structure with `graphitlive_generate_codemap`
- Measures blast radius with `graphitlive_get_impact_analysis` and `graphitlive_get_symbol_callers`
- Checks dependency cycles with `graphitlive_crawl_dependency_graph`
- Requires token-efficient TOON output whenever Graph-It-Live supports it
- Produces a concise action plan before any write-capable tool is used
- Keeps the edit scope limited to the files and symbols identified during impact analysis

## When to Use

Use this skill for refactors that involve exported signatures, moved symbols, module restructuring, dead code removal, dependency reorganization, or complex regressions.

Example prompts:

```text
Rename this exported function across the repo.
Move this class into a new services module and update callers.
Remove this public interface and clean up dependencies safely.
Refactor this package without breaking downstream imports.
```

## Requirements

- Graph-It-Live MCP tools available in the host IDE or agent runtime
- A Graph-It-Live index for the current workspace
- Native IDE editing tools for Phase 2

## Canonical MCP Tools

Use only these Graph-It-Live tool names for the pre-edit gate:

- `graphitlive_generate_codemap`
- `graphitlive_get_impact_analysis`
- `graphitlive_get_symbol_callers`
- `graphitlive_crawl_dependency_graph`

Do not rewrite them as `mcp__graph_it_live__...`, `graph-it-live...`, or semantic aliases such as `find_references` or `analyze_impact`.

## Workflow

1. Run `graphitlive_generate_codemap`, `graphitlive_get_impact_analysis`, `graphitlive_get_symbol_callers`, and `graphitlive_crawl_dependency_graph`, explicitly passing `format: "toon"` whenever supported.
2. Summarize impacted files, callers, exports, cycles, and risks.
3. Edit the primary source file.
4. Propagate changes to every impacted dependent.
5. Re-run relevant graph checks, formatters, typechecks, and tests.

## Related Skills

- [graph-it-live](../graph-it-live/) - underlying dependency intelligence toolkit
- [dead-code-hunter](../dead-code-hunter/) - ranked deletion planning for unused code
- [pr-review](../pr-review/) - Graph-It-Live evidence for Git diff review
