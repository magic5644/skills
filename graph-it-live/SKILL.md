---
name: graph-it-live
description: 'Analyze code dependencies, call graphs, and architecture using the graph-it CLI. Use when: dependency analysis, impact analysis, breaking changes, unused exports, dead code detection, call graph, symbol callers, reverse dependencies, codemap, file logic, trace execution, circular dependencies, cycle detection, refactoring safety, architecture overview, code navigation, module resolution, graph-it, graph it, dependency graph.'
argument-hint: 'What do you want to analyze in your codebase?'
---

# Graph-It-Live

AI-first dependency intelligence CLI for codebase analysis.
Analyze dependencies, call graphs, symbols, impact, and architecture from any agent-compatible IDE or CLI.

## When to Use

- Analyze file dependencies and imports
- Trace function execution across files
- Find all callers of a symbol (function, class, method)
- Detect breaking changes before refactoring
- Find unused exports / dead code
- Generate a codemap (structural overview) of any file
- Analyze intra-file call hierarchy and logic flow
- Crawl the full dependency tree from an entry point
- Find all files that import a given file (reverse lookup)
- Detect circular dependencies / cycles
- Check impact of changing a function signature
- Get a workspace architecture overview

## Quick Start — Installation

**Requires Node.js v20+.**

```bash
# Install globally
npm install -g @magic5644/graph-it-live

# Or run without installing
npx @magic5644/graph-it-live <command>
```

After global install, `graph-it` is available on PATH. Verify:

```bash
graph-it --version
```

## Supported Languages

TypeScript, JavaScript, Python, Rust, C#, Go, Java, Vue, Svelte, GraphQL.

## CLI Commands Reference

### Index the Workspace

**Always run `scan` first** to build the dependency index. All other commands depend on it.

```bash
graph-it scan
```

Re-run after significant file changes to refresh the index.

### Workspace Overview

```bash
graph-it summary                   # Full workspace overview
graph-it summary src/api.ts        # Per-file codemap
```

The per-file codemap returns: exports, internals, dependencies, dependents, call flow, cycles.

### Trace Execution Flow

Trace the complete call chain starting from a function:

```bash
graph-it trace src/index.ts#main
graph-it trace src/auth.ts#validateToken
```

Format: `<filePath>#<functionName>`. Use absolute or relative paths.

### Analyze File Logic

Show the intra-file call hierarchy — which functions call which, in what order:

```bash
graph-it explain src/server.ts
```

Returns entry points, call tree, and internal cycles.

### Dependency Graph

Crawl the full dependency tree from an entry file:

```bash
graph-it path src/index.ts
```

Shows all transitive imports and detects circular dependencies.

### Find Unused Exports

Detect dead code — exported symbols that no other file imports:

```bash
graph-it check src/api.ts
```

### Output Formats

All commands support `--format`:

| Format     | Description                                  |
|------------|----------------------------------------------|
| `text`     | Human-readable (default)                     |
| `json`     | Structured JSON                              |
| `toon`     | Token-Optimized Object Notation (30-60% smaller, best for AI) |
| `markdown` | JSON wrapped in Markdown code blocks         |
| `mermaid`  | Mermaid diagram (`trace` and `path` only)    |

```bash
graph-it summary src/api.ts --format toon
graph-it path src/index.ts --format mermaid
graph-it trace src/index.ts#main --format json
```

**Prefer `--format toon`** when consuming output programmatically — it saves 30-60% tokens.

## Advanced: MCP Tool Invocation

The CLI can invoke any of the 21 MCP tools directly:

```bash
graph-it tool --list                    # List all available tools
graph-it tool <tool_name> [--params]    # Invoke a specific tool
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `analyze_dependencies` | Direct imports and exports of a file |
| `crawl_dependency_graph` | Full dependency tree from an entry file |
| `find_referencing_files` | All files that import a given file (reverse lookup) |
| `expand_node` | Expand a node to discover dependencies beyond known paths |
| `parse_imports` | Parse raw import statements without path resolution |
| `verify_dependency_usage` | Check whether a specific import is actually used |
| `resolve_module_path` | Resolve a module specifier to an absolute file path |
| `get_symbol_graph` | Symbol-level dependencies within a file |
| `find_unused_symbols` | Dead code detection — unused exported symbols |
| `get_symbol_dependents` | All symbols that depend on a specific symbol |
| `trace_function_execution` | Full recursive call chain from a function |
| `get_symbol_callers` | All callers of a symbol (O(1) instant lookup) |
| `analyze_breaking_changes` | Detect breaking changes when modifying function signatures |
| `get_impact_analysis` | Full impact: callers + breaking changes combined |
| `get_index_status` | Current state of the dependency index |
| `invalidate_files` | Flush cache for specific files after modifications |
| `rebuild_index` | Rebuild the entire dependency index from scratch |
| `analyze_file_logic` | Intra-file call hierarchy and code flow |
| `generate_codemap` | Comprehensive structural overview of any source file |
| `query_call_graph` | BFS callers/callees via the SQLite call graph index |
| `set_workspace` | Set the project directory to analyze |

### Tool Invocation Examples

```bash
# Analyze a single file's dependencies
graph-it tool analyze_dependencies --filePath=/abs/path/to/file.ts

# Find all files importing a specific file
graph-it tool find_referencing_files --filePath=/abs/path/to/file.ts

# Get all callers of a symbol
graph-it tool get_symbol_callers --filePath=/abs/path/to/file.ts --symbolName=myFunction

# Full impact analysis
graph-it tool get_impact_analysis --filePath=/abs/path/to/file.ts --symbolName=calculateTotal

# Detect breaking changes
graph-it tool analyze_breaking_changes --filePath=/abs/path/to/file.ts --symbolName=processData

# Generate codemap
graph-it tool generate_codemap --filePath=/abs/path/to/file.ts

# Query call graph (BFS)
graph-it tool query_call_graph --symbolName=handleRequest --direction=callers --maxDepth=3
```

**Important:** Tool `--filePath` arguments require **absolute paths**.

## MCP Server Mode

Launch as an MCP server for AI client integration (no VS Code required):

```bash
graph-it serve
```

### MCP Client Configuration

**VS Code / Cursor** (`.vscode/mcp.json` or `.cursor/mcp.json`):

```json
{
  "servers": {
    "graph-it-live": {
      "type": "stdio",
      "command": "graph-it",
      "args": ["serve"],
      "env": { "WORKSPACE_ROOT": "${workspaceFolder}" }
    }
  }
}
```

**Claude Desktop** (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "graph-it-live": {
      "command": "graph-it",
      "args": ["serve"],
      "env": { "WORKSPACE_ROOT": "/path/to/project" }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add graph-it -- graph-it serve
```

**Windsurf** (`~/.codeium/windsurf/mcp_config.json`):

```json
{
  "mcpServers": {
    "graph-it-live": {
      "command": "graph-it",
      "args": ["serve"],
      "env": { "WORKSPACE_ROOT": "${workspaceFolder}" }
    }
  }
}
```

## VS Code Extension (Alternative)

Graph-It-Live is also a VS Code extension with native LM Tools for Copilot Agent mode (no MCP setup needed).

Install from Marketplace: search "Graph-It-Live" in Extensions (`Ctrl+Shift+X`).

Enable MCP server in extension: set `graph-it-live.enableMcpServer` to `true` in VS Code settings.

## Common Workflows

**"What breaks if I change this function?"**

```bash
graph-it scan
graph-it tool get_impact_analysis --filePath=/abs/path/file.ts --symbolName=myFunction
```

**"Give me an overview of this module"**

```bash
graph-it summary src/auth/index.ts --format toon
```

**"Find dead code in my project"**

```bash
graph-it check src/utils.ts
graph-it tool find_unused_symbols --filePath=/abs/path/utils.ts
```

**"Trace the execution from main()"**

```bash
graph-it trace src/index.ts#main --format mermaid
```

**"Are there circular dependencies?"**

```bash
graph-it path src/index.ts
```

Cycles are auto-detected and reported.

**"Who calls this function across the project?"**

```bash
graph-it tool get_symbol_callers --filePath=/abs/path/file.ts --symbolName=formatDate
```

## Update

```bash
graph-it update
```
