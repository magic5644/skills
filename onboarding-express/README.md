# Onboarding Express

AI-guided architectural tour of any codebase for a new developer, powered by [Graph-It-Live](../graph-it-live/).

## What It Does

In one structured pass, the AI will identify:

1. **The 3 main entry points** — where execution starts, what they orchestrate
2. **The business logic core** — which files/modules hold the real domain logic
3. **The most complex module** — highest call depth, most cycles, highest blast radius

Output is a structured report with a Mermaid diagram of the critical execution path.

## Requirements

- [Graph-It-Live](https://www.npmjs.com/package/@magic5644/graph-it-live) CLI (`npm install -g @magic5644/graph-it-live`)
- Supported languages: TypeScript, JavaScript, Python, Rust, C#, Go, Java, Vue, Svelte

## Installation

```bash
npx skills add magic5644/skills/onboarding-express
```

Or copy manually to your agent's skill directory.

## Usage

Trigger with natural language in your agent:

> "Give me a guided tour of this project"
> "I'm new to this codebase, where do I start?"
> "Show me the entry points and business logic"
> "Which module is the most complex?"

## Related Skills

- [graph-it-live](../graph-it-live/) — underlying dependency analysis engine
- [dead-code-hunter](../dead-code-hunter/) — clean up orphan code before onboarding
