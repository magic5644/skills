# Graph-It-Live PR Review

Review a pull request or branch diff with deterministic Graph-It-Live evidence: breaking signatures,
dependent symbols, cycles, unused exports, test candidates, risk score, and explicit limitations.

## What It Does

- Runs `graph-it review-pr` against a Git base ref
- Classifies the highest changed-symbol risk as low, medium, high, or critical
- Surfaces evidence for API breaks, dependency impact, cycles, unused exports, and test candidates
- Escalates significant symbols through caller and impact analysis
- Produces a merge-ready review with limitations stated explicitly
- Provides a reusable GitHub Actions review gate with optional blocking threshold

## Requirements

- [Graph-It-Live](https://www.npmjs.com/package/@magic5644/graph-it-live) CLI
- Node.js v22+
- A Git repository with the base ref available locally

## Installation

```bash
npx skills add magic5644/skills/pr-review
```

## Usage

Trigger the skill with natural language:

> "Review this PR before merge"
> "Analyze my branch against main"
> "Is this diff safe to merge?"
> "Add a Graph-It-Live PR review gate"

Run the local command directly when preferred:

```bash
git fetch origin main
graph-it review-pr --base origin/main --format markdown
```

Use bounded structured output for agent analysis:

```bash
graph-it review-pr --base origin/main --head HEAD --depth 3 --max-files 200 --format toon
```

A result with `isPartial: true` or non-empty `limitations` requires manual follow-up. No detected
breaking signature does not prove the diff has no behavioral risk.

## GitHub Actions Gate

```yaml
name: Graph-It Review Gate

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: magic5644/Graph-It-Live/.github/actions/graph-it-review-gate@v1.13.0
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          comment: ${{ github.event.pull_request.head.repo.fork && 'false' || 'true' }}
          fail-on-risk: high
```

The action emits `risk`, `score`, and `cli-version`. Set `comment: false` and remove
`pull-requests: write` when a sticky PR comment is not required. Keep comments disabled for fork PRs.

## Related Skills

- [graph-it-live](../graph-it-live/) — dependency, call-graph, and architecture analysis
- [dead-code-hunter](../dead-code-hunter/) — safe cleanup candidates before a review
- [onboarding-express](../onboarding-express/) — architecture tour before making a risky change
