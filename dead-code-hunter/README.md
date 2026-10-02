# Dead Code Hunter

Scan your dependency graph for orphan symbols and ghost files, then get a ranked, safety-annotated deletion plan.
Powered by [Graph-It-Live](../graph-it-live/).

## What It Does

- Surfaces candidate unused exports and unreferenced files for evidence-based review
- Identifies **ghost files** (files not imported anywhere, not an entry point)
- Requires incoming-reference checks for candidate symbols, including type-only references when supported; zero call sites alone never confirms dead code
- Classifies candidates as **unconfirmed**, **manual review**, or **do not delete**
- Produces a **prioritized review plan**; missing reference evidence never yields a deletion recommendation

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

Use CLI capabilities as advertised by the installed release. The observed CLI help describes
`graph-it check` as file-scoped. If `graph-it tool --list` advertises `scan_dead_code`, use it for
workspace discovery; do not assume it supports a scope parameter:

```bash
graph-it scan
graph-it tool scan_dead_code
```

Before recommending deletion, confirm incoming symbol references/dependents—including type-only
references when supported—and incoming file references using capabilities actually advertised by
the CLI or the MCP host's tool schema. A call-sites-only result is insufficient. Missing or partial
confirmation means the candidate remains unconfirmed; do not recommend deletion. For MCP, use
only structurally equivalent host-advertised tools and their exact input schemas.

## Limitations

- Dynamic dispatch (`obj[method]()`, `require(variable)`) is invisible to static analysis
- Framework decorators (`@Component`, `@Injectable`) may produce false positives
- Published library exports may appear "unused" but are part of the public API

## Related Skills

- [graph-it-live](../graph-it-live/) — underlying dependency analysis engine
- [onboarding-express](../onboarding-express/) — use Dead Code Hunter before onboarding a new developer
- [pr-review](../pr-review/) — review cleanup diffs before merge
