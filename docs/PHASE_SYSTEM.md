# Phase System: 3-Stage Robustness Pipeline

This document explains the three-phase system that ensures accuracy, memory persistence, and verification for every OpenCode session.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPENCODE SESSION START                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: SETUP VERIFICATION                                    │
│  ✓ Node.js 20+ installed                                        │
│  ✓ OpenCode installed and in PATH                               │
│  ✓ NVIDIA_API_KEY set (nvapi- format, 45+ chars)               │
│  ✓ OpenCode config points to Nemotron 3 Ultra                  │
│  ✓ Memory structure exists                                      │
│  ✓ Project structure initialized                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: MEMORY & PROMPT ACTIVATION                            │
│  ✓ Load global memory (memory/global/MEMORY.md)                │
│  ✓ Load project memory (projects/<name>/MEMORY.md)             │
│  ✓ Load official limitations (docs/00-limitations.md)          │
│  ✓ Load recent cache context                                    │
│  ✓ Build complete system prompt                                 │
│  ✓ Write activation files to project cache                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: DUAL-VERIFICATION ACCURACY LAYER                     │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │   PASS 1        │  │   PASS 2        │                      │
│  │ (Standard)      │  │ (Stricter)      │                      │
│  ├─────────────────┤  ├─────────────────┤                      │
│  │ No hallucination│  │ Re-verify all   │                      │
│  │ Scope compliance│  │ + Consistency   │                      │
│  │ Factual check   │  │   with Pass 1   │                      │
│  │ Code safety     │  │                 │                      │
│  │ Format compliance                   │                      │
│  └─────────────────┘  └─────────────────┘                      │
│        │                  │                                      │
│        └────────┬────────┘                                      │
│                 ▼                                               │
│         FINAL VERDICT                                           │
│         (Both must pass)                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OPENCODE READY                               │
│  • System prompt injected                                       │
│  • Memory active                                                │
│  • Verification enabled                                         │
│  • Project context loaded                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Windows PowerShell
```powershell
# Full run (recommended first time)
.\scripts\opencode_runner.ps1 my-project

# Skip Phase 1 (if already verified)
.\scripts\opencode_runner.ps1 my-project -SkipPhase1

# Test verification only
.\scripts\opencode_runner.ps1 my-project -VerifyOnly

# Initialize and run
.\scripts\opencode_runner.ps1 new-project -Init
```

### macOS / Linux
```bash
# Full run
python scripts/opencode_runner.py my-project

# Skip Phase 1
python scripts/opencode_runner.py my-project --skip-phase1

# Verify only
python scripts/opencode_runner.py my-project --verify-only

# Initialize and run
python scripts/opencode_runner.py new-project --init
```

## Phase Details

### Phase 1: Setup Verification (`scripts/phase1_verify.py`)

**What it checks:**
| Check | Requirement |
|-------|-------------|
| Node.js | v20+ LTS |
| OpenCode | Installed via npm, in PATH |
| API Key | `NVIDIA_API_KEY` env var, starts with `nvapi-`, 45+ chars |
| Config | `~/.config/opencode/opencode.json` with correct model |
| Memory | `memory/global/MEMORY.md` exists |
| Project | `projects/<name>/` with MEMORY.md, input/, output/, cache/ |

**Run manually:**
```bash
python scripts/phase1_verify.py my-project
```

**Exit codes:** 0 = all pass, 1 = errors found

### Phase 2: Memory Activation (`scripts/phase2_activate.py`)

**What it does:**
1. Reads global memory (`memory/global/MEMORY.md`)
2. Reads project memory (`projects/<name>/MEMORY.md`)
3. Reads official limitations (`docs/00-limitations.md`)
4. Loads recent cache entries (last 5)
5. Builds complete system prompt with all context
6. Writes to project cache:
   - `cache/system_prompt.md`: Full system prompt
   - `cache/opencode_init.js`: OpenCode initialization script
   - `cache/activation_summary.json`: Metadata

**System prompt includes:**
- Core rules (solution-first, no em-dashes, confirm before write, etc.)
- Global memory (user profile, preferences, cross-project rules)
- Project memory (project-specific context, rules, history)
- Official model limitations (free tier limits, benchmarks, hardware reqs)
- Recent cache context
- Project structure paths
- Workflow triggers (sync, push to local, push to git, force)
- Visual marker specifications

**Run manually:**
```bash
python scripts/phase2_activate.py my-project
```

### Phase 3: Dual Verification (`scripts/phase3_verify.py`)

**Pass 1 Checks (Standard):**
| Check | Description | Threshold |
|-------|-------------|-----------|
| Hallucination | No "as an AI language model", "knowledge cutoff", etc. | 0 markers |
| Scope | Response length appropriate for request | ≤5x (answers), ≤20x (code) |
| Factual | Claims verified against loaded sources | ≥50% claims supported |
| Code Safety | No eval, exec, shell=True, pickle, etc. | 0 unsafe patterns |
| Format | No em-dashes, no preambles, concise | 0 violations |

**Pass 2 Checks (Stricter):**
- Re-runs all Pass 1 with 10% higher confidence requirement
- Adds consistency check: Pass 1 must have passed

**Final Verdict:** Both passes must pass for response to be approved.

**Run manually (test):**
```bash
python scripts/phase3_verify.py
```

## Integration with OpenCode

The runner (`scripts/opencode_runner.py`) automatically:

1. Runs Phase 1 (unless `--skip-phase1`)
2. Runs Phase 2, generates system prompt
3. Sets environment variables for OpenCode:
   - `NEMOTRON_PROJECT` = project name
   - `NEMOTRON_SYSTEM_PROMPT` = path to system prompt
   - `NEMOTRON_INIT_SCRIPT` = path to init script
4. Changes to project directory
5. Launches `opencode`

### How OpenCode Uses the System Prompt

When OpenCode starts, it reads the system prompt from the environment. The Phase 2 generated prompt includes instructions for the model to:

1. **Self-verify** before responding (internal Phase 3)
2. **Check twice** - explicitly reason through verification steps
3. **Reference memory** - cite global/project memory when relevant
4. **Stay accurate** - prefer "uncertain" over guessing

### Manual OpenCode Integration

If not using the runner, add to your OpenCode config:

```json
{
  "agent": {
    "build": {
      "systemPromptFile": "projects/my-project/cache/system_prompt.md"
    }
  }
}
```

Or source the init script in your shell before running opencode.

## Verification Logs

Each verification creates a log in `projects/<name>/cache/`:
- `verification_YYYYMMDD_HHMMSS.json`: Full pass details
- `activation_summary.json`: Phase 2 metadata

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Phase 1 fails | Run individual checks: `python scripts/phase1_verify.py <project>` |
| Memory not loading | Check `projects/<name>/MEMORY.md` exists and is readable |
| Verification too strict | Adjust thresholds in `scripts/phase3_verify.py` |
| OpenCode doesn't use prompt | Verify `NEMOTRON_SYSTEM_PROMPT` env var is set |

## Customization

### Add Custom Verification Checks

Edit `scripts/phase3_verify.py`, add method to `Phase3Verifier`:

```python
def verify_my_rule(self, response: str) -> VerificationResult:
    # Your logic
    return VerificationResult(...)
```

Add to `run_all_verifications()`.

### Add Custom Memory Sources

Edit `scripts/phase2_activate.py`, modify `build_system_prompt()`:

```python
custom = self.load_file(ROOT / "my" / "custom.md")
if custom:
    parts.append(f"\n## CUSTOM CONTEXT\n{custom}")
```

### Per-Project Configuration

Create `projects/<name>/.phase-config.json`:

```json
{
  "skip_phase1": false,
  "verification_strictness": "high",
  "custom_prompt_additions": "projects/my-project/custom_prompt.md"
}
```

## Files Created Per Session

```
projects/<name>/
├── MEMORY.md                 # Project memory (persistent)
├── input/                    # Your input files
├── output/                   # Generated outputs
└── cache/
    ├── system_prompt.md      # Phase 2: Full system prompt
    ├── opencode_init.js      # Phase 2: OpenCode init script
    ├── activation_summary.json
    └── verification_*.json   # Phase 3: Verification logs
```

## Best Practices

1. **Always run full pipeline first time**: Don't skip Phase 1
2. **Update project memory**: After significant work, update `projects/<name>/MEMORY.md`
3. **Run verify-only periodically**: `opencode_runner.py --verify-only` catches regressions
4. **Check verification logs**: Review `cache/verification_*.json` for patterns
5. **Keep global memory current**: Update `memory/global/MEMORY.md` with cross-project learnings