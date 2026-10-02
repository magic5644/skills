# Graph-It Refactor

Safe two-phase refactoring for agentic coding workflows. It requires semantic impact evidence from Graph-It-Live before code is edited, without assuming a fixed CLI or MCP tool inventory.

## What It Does

- Prefers the installed `graph-it` CLI when it can perform the needed analysis; falls back to host-advertised MCP tools when the CLI is unavailable or unsuitable
- Maps target structure, exported-symbol impact, callers, importers/reference coverage, cycles, and transitive dependencies using observed capabilities
- Requires the workspace index to be scanned before graph analysis
- Uses TOON output only when the discovered CLI command or MCP schema supports it
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

## Tool discovery and requirements

At first activation of a Graph-It skill in a session, inspect `graph-it --version`, `graph-it tool --list`, and `graph-it --help` once when the CLI and terminal are available; otherwise inspect the host's advertised MCP inventory. Reuse and share that session inventory across Graph-It skills; refresh only after a version/executable/workspace change or a capability failure. The installed CLI inventory and the host's advertised MCP inventory—not this README—are authoritative.

The environment must expose an index-scan capability and Graph-It capabilities sufficient for the evidence this refactor needs, through either the CLI or MCP. Native IDE editing tools are needed for Phase 2. If the scan or required evidence is unavailable, stop before editing and report the gap.

If CLI analysis is unavailable or unsuitable, use only MCP tools advertised by the host, with their exact namespace/name and `inputSchema`. CLI aliases are not guaranteed to be MCP tools. Use `response_format: "toon"` only when the schema supports it. For CLI, use `--format toon` only if the discovered command supports it. The CLI's `tool` commands invoke analysis directly; `graph-it serve` starts an MCP server.

Examples of useful capabilities, only when exposed, include:

- `generate_codemap` for target structure
- `get_impact_analysis` for exported-symbol impact
- `query_call_graph --direction=callers --depth=1` for caller evidence
- `crawl_dependency_graph` for cycles and transitive effects

These are examples, not a required list or guaranteed interface. Confirm actual availability and invocation syntax from the discovered CLI inventory/help or exact host MCP inventory/schema. Caller evidence alone does not prove importer or complete reference coverage. A discovered `graph_context` or other capability is suitable only if it returns equivalent evidence for the requirement.

If the CLI itself announces a newer version at the first Graph-It skill activation, request explicit confirmation before `graph-it update` in interactive sessions. Default to yes only in automatic mode that is explicitly enabled and pre-authorized. Silence, timeout, non-TTY execution, and Agent mode alone are not consent. Do not update without a notice, install implicitly, or poll for releases. After success, re-check version and inventory; restarting a running MCP server requires host authorization. If update fails, keep using the available CLI and report the failure briefly without retries or escalation.

## Workflow

1. Identify target files and scan the workspace index using the discovered CLI or MCP capability. If no scan capability is available, stop and report the blocker.
2. Map required evidence—structure, exported-symbol impact, callers, importers/reference completeness, cycles, and transitive dependencies—to capabilities actually available. Report gaps in dynamic dispatch, generated code, type-only references, public APIs, or language coverage.
3. Stop before editing if required evidence is missing, blocked, or partial. Search tools such as `rg` can locate files but cannot replace Graph-It-Live evidence.
4. Present a concise plan naming files, changes, impacted callers/importers/references/exports, and risks or coverage gaps.
5. Edit only the planned scope, propagate the changes, then run relevant graph checks, formatters, type checks, and tests.

## Related Skills

- [graph-it-live](../graph-it-live/) - underlying dependency intelligence toolkit
- [dead-code-hunter](../dead-code-hunter/) - ranked deletion planning for unused code
- [pr-review](../pr-review/) - Graph-It-Live evidence for Git diff review
