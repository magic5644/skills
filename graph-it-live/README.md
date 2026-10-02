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
- **PR review** — Risk-score a Git diff for API breaks, impact, cycles, and test candidates
- **Tool discovery** — Inspect installed CLI analysis tools with `graph-it tool --list`
- **Natural language query** via `graph-it query`
- **Markdown wiki generation** via `graph-it wiki`
- **Session telemetry** via `graph-it stats`

## Supported Languages

TypeScript, JavaScript, Python, Rust, C#, Go, Java, Vue, Svelte, GraphQL.

---

## Prerequisites

- **Node.js v22+**

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

# 6. Ask a natural-language architecture question
graph-it query "how does authentication flow through this codebase"

# 7. Review a Git diff before merging
graph-it review-pr --base origin/main --format markdown

# 8. Generate markdown wiki docs from call graph
graph-it wiki
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
| `path-in <file>` | Incoming dependencies | `graph-it path-in src/api.ts` |
| `check-dependencies <file>` | Incoming and outgoing dependencies | `graph-it check-dependencies src/api.ts` |
| `cycles <file>` | Confirmed dependency cycles | `graph-it cycles src/api.ts` |
| `architecture` | Full workspace architecture | `graph-it architecture --format toon` |
| `check <file>` | Unused exported symbols | `graph-it check src/api.ts` |
| `review-pr` | Review a Git diff with risk scoring | `graph-it review-pr --base origin/main --format markdown` |
| `query "<question>"` | Natural language codebase query | `graph-it query "what calls Spider"` |
| `wiki` | Generate markdown wiki from call graph | `graph-it wiki` |
| `stats` | TOON and LLM session telemetry | `graph-it stats` |
| `serve` | Launch MCP stdio server | `graph-it serve` |
| `tool <name>` | Invoke an advertised analysis tool directly through the CLI | `graph-it tool get_index_status` |
| `update` | Update to latest version | `graph-it update` |

`graph-it tool --list` is the installed CLI's authoritative textual inventory; it can change
between releases. `graph-it tool <name>` invokes analysis directly through the CLI, while
`graph-it serve` starts the MCP server. In MCP mode, use only tools and parameters advertised by
the connected host; its schema may differ from the CLI inventory. CLI `--format` and MCP
`response_format` are separate interfaces.

CLI output formats are command-specific; consult `graph-it --help` or command help:

| Format | Description | Availability |
| ------ | ----------- | ------------ |
| `text` | Human-readable (default) | Commands that advertise `--format` |
| `json` | Structured JSON | Commands that advertise `--format` |
| `toon` | Token-Optimized (30-60% smaller) | Commands that advertise `--format` |
| `markdown` | Markdown output | Commands that advertise `--format` |
| `mermaid` | Mermaid diagram | `trace`, `path` only |

---

## MCP Server Integration

Graph-It-Live can run as an MCP server for direct AI client integration:

```bash
graph-it serve
```

See `SKILL.md` for full MCP client configuration for VS Code, Cursor, Claude Desktop, Claude Code CLI, and Windsurf.

For MCP calls, the connected host's advertised tool schema is authoritative; use output options
such as `response_format` only when that schema supports them.

---

## CLI Analysis Tools (`graph-it tool`)

Discover installed CLI tools with `graph-it tool --list` and consult CLI help for parameters.
Examples elsewhere in this README illustrate usage; they are not a canonical tool whitelist.

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
Review the changes between my branch and main before I merge
```

## Pull Request Review

Run a local, deterministic review from the repository root:

```bash
graph-it review-pr --base origin/main --format markdown
```

The result reports a `risk` level, a `score`, changed symbols, evidence, test candidates, and any
`limitations`. A partial result is not a clean review: investigate its limitations before merging.

For a reusable agent workflow and a GitHub Actions gate, install
[pr-review](../pr-review/).

### VS Code / GitHub Copilot

The skill works directly in Copilot Agent mode. The graph-it VS Code extension also provides native LM Tools (no MCP setup required), including dependency, call graph, dead-code, breaking-change, and natural-language query tools.

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
