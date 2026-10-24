---
name: graph-it-refactor
description: Use when refactoring multiple files, changing exported signatures or interfaces, moving symbols, deleting dead code, reorganizing dependencies, or fixing complex regressions.
---

# Graph-It Refactor

Safe two-phase refactoring for changes whose blast radius is larger than one local implementation detail.
Map semantic impact with Graph-It-Live before editing code with the host IDE's native tools. Prefer an installed `graph-it` CLI when it can perform the analysis; use host-provided MCP tools when the CLI is unavailable or unsuitable.

## Discover available tools

At the first activation of a Graph-It skill in a session, discover CLI capabilities once if the `graph-it` executable and terminal are available; otherwise use the host's advertised MCP inventory:

```text
graph-it --version
graph-it tool --list
graph-it --help
```

Keep this inventory in session context and share it across Graph-It skills. Do not repeat discovery for each command or skill; refresh only if the executable/version or workspace context changes, or a capability fails or is reported unavailable. The installed inventory and host-advertised MCP inventory are authoritative. Do not assume fixed tool names, counts, versions, or latest remote releases.

If the installed CLI's normal notice says a newer version is available, handle it only at the first Graph-It skill activation in the session. In an interactive session, ask for explicit confirmation before running `graph-it update`. Default to yes only in automatic mode that is explicitly enabled and pre-authorized; silence, timeout, non-TTY execution, and Agent mode alone are not consent. Do not update without a notice, install implicitly, or poll independently for releases. After a successful update, re-read the version and CLI inventory. An already-running MCP server may need a host-authorized restart to use the new binary; do not edit MCP configuration. If the update fails, retain the usable CLI and report the failure briefly without retrying or escalating privileges.

This skill requires Graph-It-Live CLI **1.21.0 or later**. Compare the reported `graph-it --version` with 1.21.0 at the same first activation. If it is older, say so once, name the commands it lacks, and offer `graph-it update` under the confirmation policy above; until it is updated, use only commands listed by that CLI's `--help` and `tool --list`. If the version cannot be read, treat it as older.

The CLI's `tool` commands invoke analysis directly; `graph-it serve` starts an MCP server. Do not treat direct CLI analysis as MCP, and do not start or reconfigure a server just to work around a missing CLI capability. CLI aliases are not guaranteed to be MCP tools. If using MCP, call only tools advertised by the host, with their exact advertised namespace/name and `inputSchema` parameters. Use `response_format: "toon"` only when that schema supports it. For CLI output, use `--format toon` only when the discovered command supports that option. Never guess tool names, aliases, schemas, flags, or JSON output formats.

## When to Use

- A refactor touches multiple files or modules.
- An exported function, class, method, type, interface, or package entry point changes name, location, signature, or visibility.
- Code is being moved between files, folders, packages, or layers.
- Dead code removal or dependency reorganization could affect callers, imports, or package exports.
- A complex regression may be caused by call graph, dependency, or module-boundary changes.

## Phase 1: Semantic Mapping and Impact Analysis

This phase is source-read-only. Do not edit source, run formatters or codemods, or use package managers or shell commands that alter the worktree. First identify the target file(s); if unknown, use read-only search or IDE navigation to resolve them. Search results help locate targets but never replace semantic evidence.

Before graph analysis, scan the workspace index using `graph-it scan` if supported by the installed CLI, or the exact host-advertised MCP scan capability for MCP-only use. If neither route can scan the index, stop and report that prerequisite rather than analyzing an unknown or stale index. Index refresh must not modify source files.

### Required evidence gate

Resolve these evidence needs to capabilities actually present in the CLI inventory or host MCP inventory. Use the CLI where suitable; fall back to MCP only when the CLI is unavailable or unsuitable. Illustrative capability names—not a required or exhaustive tool list—include `generate_codemap`, `get_impact_analysis`, `query_call_graph --direction=callers --depth=1`, and `crawl_dependency_graph`, but use them only when actually exposed and invoke them with discovered syntax and supported parameters.

Obtain and assess evidence appropriate to the change:

- Target structure: relevant files/modules, definitions, and exports.
- Exported-symbol impact: affected exported symbols and their impact across the workspace.
- Callers and references: caller evidence, importer/dependent evidence, and whether reference coverage is complete. Do not treat callers as proof of all references or importers.
- Dependency effects: cycles and transitive dependencies across the touched area.

`query_call_graph` with caller direction and depth one is an example for caller evidence only; it does not establish importer or complete reference coverage. A discovered `graph_context` or other capability is an acceptable alternative only if its returned evidence is equivalent for the requirement being met. Report dynamic dispatch, reflection, generated code, type-only references, public API surfaces, unsupported languages, and other known coverage gaps.

If a capability needed for the applicable evidence is unavailable, blocked, or returns partial/incomplete results, stop before editing and report the gap. Do not use `rg`, IDE references, or tests as a substitute for missing graph evidence. Do not claim complete references, callers, or importers unless the observed capability and result support that claim.

Before editing, present a concise plan naming the files and intended changes, impacted callers/importers/references/dependent symbols/exports, cycles and transitive effects, and any remaining risks or coverage gaps. Omitting this plan means Phase 1 is incomplete.

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
| Observed capabilities | Select commands/tools and parameters from the discovered CLI inventory/help or exact host-advertised MCP names and schemas. |
| Efficient output | Use CLI `--format toon` or MCP `response_format: "toon"` only when the relevant command/tool supports it. |
| No blind editing | Do not edit until all evidence required for the change is available and assessed. |
| Evidence completeness | Treat missing or partial caller, importer, reference, impact, or dependency evidence as a blocker when required; do not infer completeness. |
| Sealed scope | Do not broaden the refactor beyond files and symbols identified during Phase 1. |
| Cycle awareness | Establish cycles and transitive dependency effects for the touched area before moves, deletions, signature changes, or module reorganizations. |
| Update consent | Never update without the stated notice and required explicit authorization; never treat silence or non-interactive execution as consent. |

## Common Mistakes

- Running `rg` only and assuming text matches are a complete impact analysis.
- Repeating CLI discovery for every command or hard-coding a remembered tool inventory as current authority.
- Assuming an MCP tool name, namespace, schema, CLI alias, flag, or output format without discovering it.
- Treating caller results as complete importer/reference evidence.
- Using a graph context result without confirming it meets the particular evidence requirements.
- Claiming a complete analysis despite missing language, dynamic-dispatch, generated-code, or public-API coverage.
- Updating or installing the CLI without the required notice and consent.
- Claiming a narrow diff removes the need for impact or cycle analysis.
- Moving a public symbol without checking package exports, barrel files, and compatibility re-exports.
- Editing first, then using Graph-It-Live to justify the diff afterward.

## Red Flags

- "This is urgent, just rename it."
- "The references are obvious."
- "Tests are already red, so impact analysis can wait."
- "No need for a full architecture pass."
- "I'll fix imports after the move."
- "I remember this tool name/schema from another host, so it must be available here."
- "Caller results prove every importer and reference."
- "No CLI is installed, so I'll silently install or update it."

These all mean: stop, complete Phase 1, and resolve the evidence or consent gap before editing.
