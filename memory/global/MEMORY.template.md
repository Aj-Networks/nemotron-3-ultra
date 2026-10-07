# Global Memory (Shared Across All Projects)

This file contains persistent knowledge, preferences, and rules that apply to ALL projects using this Nemotron 3 Ultra setup.

## User Profile

- **Name**: [Your Name]
- **Primary Use Cases**: Coding, research, analysis, documentation
- **Preferred Languages**: Python, TypeScript, SQL, PowerShell
- **Editor**: VS Code / OpenCode terminal
- **OS**: Windows 11 (primary), Linux/macOS (secondary)

## Global Preferences

- **Response Style**: Concise, solution-first, minimal preamble
- **Code Style**: Type hints, docstrings, error handling, no em-dashes
- **Commit Messages**: Imperative, under 70 chars, unique subject
- **Testing**: Verify before commit. Run lint/typecheck if available.
- **Security**: Never commit secrets. Use env vars for API keys.

## Cross-Project Rules

1. **Memory isolation**: Each project has own `projects/<name>/MEMORY.md`
2. **Global wins on conflicts** unless project explicitly overrides
3. **Cache sharing**: Global cache in `cache/global/`, project cache in `cache/projects/<name>/`
4. **Session sync**: Run `sync` command at session start to pull latest

## API Key Management

- **Primary**: `NVIDIA_API_KEY` (env var, free tier at build.nvidia.com)
- **Fallback**: `OPENROUTER_API_KEY` (for `nvidia/nemotron-3-ultra-550b-a55b:free`)
- **Rotation**: Monthly or on 429 errors
- **Never in config files**: Always `{env:VAR_NAME}`

## Model Configuration Defaults

```json
{
  "model": "nvidia/nvidia/nemotron-3-ultra-550b-a55b",
  "provider": "nvidia",
  "temperature": 1.0,
  "top_p": 0.95,
  "max_tokens": 32000,
  "reasoning_budget": 1024,
  "enable_thinking": true,
  "force_nonempty_content": true
}
```

## Known Working Configs

- OpenCode config: `~/.config/opencode/opencode.json` (see examples/)
- Windows PowerShell: `setx NVIDIA_API_KEY "nvapi-..."`
- Node.js: v20+ LTS required for OpenCode

## Troubleshooting Quick Ref

| Error | Fix |
|-------|-----|
| 401 Unauthorized | Regenerate API key at build.nvidia.com |
| 429 Rate Limited | Wait 60s, reduce concurrency, check quota |
| Context length exceeded | Reduce input, enable chunked prefill |
| Reasoning loops | Set `reasoning_budget: 512` |
| Tool call failures | Add `force_nonempty_content: true` |

---

*Edit this file to persist global knowledge across sessions.*