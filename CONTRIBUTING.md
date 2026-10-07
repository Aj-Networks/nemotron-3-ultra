# Contributing

## Quick Rules

1. **No em-dashes**: Use periods, colons, parentheses, or "and"
2. **Blunt, short wording**: Solution first, education second
3. **Test before commit**: Run lint/typecheck if available
4. **Never commit secrets**: API keys, tokens, passwords

## Workflow

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make changes (follow existing code style)
4. Verify: run setup scripts, test memory manager
5. Commit with imperative message: `add rate limiter config`
6. Push and open PR

## Code Style

- Python: type hints, docstrings, 4-space indent
- PowerShell: PascalCase functions, comment-based help
- Bash: lowercase functions, `set -euo pipefail`
- JSON: 2-space indent, trailing commas where valid
- Markdown: no em-dashes, concise sentences

## Areas Welcome

- Additional provider configs (OpenRouter, local vLLM, etc.)
- More memory/cache backends (SQLite, Redis, PostgreSQL)
- Additional monitoring dashboards
- Windows/macOS/Linux setup improvements
- Documentation translations
- Screenshot contributions for website

## Not Accepted

- Changes to model IDs or technical specs without source
- Em-dashes in any file
- Secrets or real API keys
- Breaking changes without version bump