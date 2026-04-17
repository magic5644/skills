# Graph-It-Live Skill

**Analyze code dependencies, call graphs, and architecture using the graph-it CLI — from any AI agent-compatible IDE.**

Graph-It-Live is an AI skill that gives your coding agent full access to the [graph-it CLI](https://www.npmjs.com/package/@magic5644/graph-it-live), a powerful dependency intelligence tool for codebase analysis.

---

## Features

- **Dependency analysis** — File-level import/export relationships
- **Call graph** — Cross-file symbol call relationships
- **Execution tracing** — Full recursive call chain from any function
- **Impact analysis** — Detect breaking changes before refactoring
- **Dead code detection** — Find unused exported symbols
- **Codemap generation** — Structural overview of any source file
- **File logic analysis** — Intra-file call hierarchy and code flow
- **Cycle detection** — Circular dependency identification
- **Reverse lookup** — Find all files importing a given file
- **21 MCP tools** — Full analysis engine exposed to AI assistants

## Supported Languages

TypeScript, JavaScript, Python, Rust, C#, Go, Java, Vue, Svelte, GraphQL.

---

## Prerequisites

- **Node.js v20+**

---

## Installation

### Install the CLI

```bash
# Global install
npm install -g @magic5644/graph-it-live

# Or use without installing
npx @magic5644/graph-it-live <command>
```

### Install the Skill

Using the [skills CLI](https://www.npmjs.com/package/skills):

```bash
npx skills add magic5644/skills/graph-it-live
```

Or manually:

**VS Code / GitHub Copilot:**

```bash
mkdir -p ~/.copilot/skills/graph-it-live
cp -r . ~/.copilot/skills/graph-it-live/
```

**Claude Code:**

```bash
mkdir -p ~/.claude/skills/graph-it-live
cp -r . ~/.claude/skills/graph-it-live/
```

**Generic agents (Cursor, Cline, etc.):**

```bash
mkdir -p ~/.agents/skills/graph-it-live
cp -r . ~/.agents/skills/graph-it-live/
```

---

## Quick Start

```bash
# 1. Index the workspace (required first)
graph-it scan

# 2. Get a workspace overview
graph-it summary

# 3. Analyze a specific file
graph-it summary src/api.ts

# 4. Trace execution from a function
graph-it trace src/index.ts#main

# 5. Find unused exports
graph-it check src/utils.ts
```

---

## CLI Commands

| Command | Description | Example |
| ------- | ----------- | ------- |
| `scan` | Index/re-index the workspace | `graph-it scan` |
| `summary [file]` | Workspace overview or per-file codemap | `graph-it summary src/api.ts` |
| `trace <sym>` | Trace execution flow | `graph-it trace src/index.ts#main` |
| `explain <file>` | Intra-file call hierarchy | `graph-it explain src/server.ts` |
| `path <file>` | Dependency graph from entry file | `graph-it path src/index.ts` |
| `check <file>` | Unused exported symbols | `graph-it check src/api.ts` |
| `serve` | Launch MCP stdio server | `graph-it serve` |
| `tool <name>` | Invoke any MCP tool directly | `graph-it tool get_index_status` |
| `update` | Update to latest version | `graph-it update` |

### Output Formats

All commands support `--format`:

| Format | Description | Availability |
| ------ | ----------- | ------------ |
| `text` | Human-readable (default) | All commands |
| `json` | Structured JSON | All commands |
| `toon` | Token-Optimized (30-60% smaller) | All commands |
| `markdown` | Markdown-wrapped JSON | All commands |
| `mermaid` | Mermaid diagram | `trace`, `path` only |

---

## MCP Server Integration

Graph-It-Live can run as an MCP server for direct AI client integration:

```bash
graph-it serve
```

See `SKILL.md` for full MCP client configuration for VS Code, Cursor, Claude Desktop, Claude Code CLI, and Windsurf.

---

## 21 MCP Tools

| Tool | Description |
| ---- | ----------- |
| `analyze_dependencies` | Direct imports and exports of a file |
| `crawl_dependency_graph` | Full dependency tree from an entry file |
| `find_referencing_files` | Reverse dependency lookup |
| `expand_node` | Expand dependencies beyond known paths |
| `parse_imports` | Raw import statements |
| `verify_dependency_usage` | Check if an import is actually used |
| `resolve_module_path` | Resolve module specifier to absolute path |
| `get_symbol_graph` | Symbol-level dependencies within a file |
| `find_unused_symbols` | Dead code detection |
| `get_symbol_dependents` | Symbols depending on a given symbol |
| `trace_function_execution` | Full recursive call chain |
| `get_symbol_callers` | All callers of a symbol (O(1) lookup) |
| `analyze_breaking_changes` | Breaking change detection |
| `get_impact_analysis` | Full impact: callers + breaking changes |
| `get_index_status` | Dependency index status |
| `invalidate_files` | Flush cache for specific files |
| `rebuild_index` | Full index rebuild |
| `analyze_file_logic` | Intra-file call hierarchy |
| `generate_codemap` | Comprehensive file structural overview |
| `query_call_graph` | BFS callers/callees via SQLite index |
| `set_workspace` | Set project directory to analyze |

---

## Using with AI Agents

The skill is **automatically invoked** when you ask architecture or dependency-related questions.

### Example Prompts

```text
What breaks if I change the calculateTotal function in src/billing.ts?
Show me the architecture of the auth module
Find all callers of formatDate across the project
Are there circular dependencies starting from src/index.ts?
Generate a codemap for src/api/server.ts
Find dead code in src/utils.ts
Trace the execution flow from main() in src/index.ts
What files depend on src/models/User.ts?
```

### VS Code / GitHub Copilot

The skill works directly in Copilot Agent mode. The graph-it VS Code extension also provides 20 native LM Tools (no MCP setup required).

### Claude Code

```bash
claude "Analyze the impact of changing processData in src/api.ts"
claude "Find unused exports in src/utils/"
```

---

## Project Structure

```text
graph-it-live/
├── README.md
└── SKILL.md
```

---

## License

MIT — Free to use, modify, and redistribute.
