# Nemotron 3 Ultra + OpenCode: Production-Ready Setup

Run NVIDIA's **Nemotron 3 Ultra (550B-A55B)** as a coding assistant in your terminal using **OpenCode** and NVIDIA's **free API**. Includes memory system, caching, project isolation, rate limiting, and monitoring for production scale.

## Quick Start (Windows PowerShell): With Full Phase Verification

```powershell
# 1. Clone or download this repo
cd nemotron-3-ultra

# 2. Run automated setup (prompts for API key securely)
.\scripts\setup-windows.ps1 -ProjectName my-project

# 3. Close and reopen PowerShell, then run with full Phase 1-3 pipeline:
python scripts/opencode_runner.py my-project
# Or use the PowerShell wrapper:
.\scripts\opencode_runner.ps1 my-project
```

### Phase Pipeline (Runs Automatically)
1. **Phase 1**: Verifies Node.js, OpenCode, API key, config, memory structure
2. **Phase 2**: Loads global/project memory, limitations, builds system prompt
3. **Phase 3**: Dual-verification: every response checked twice before output
4. **OpenCode**: Launches with full context active

## Quick Start (macOS / Linux): With Full Phase Verification

```bash
cd ~/OneDrive/AI/nemotron 3 ultra
chmod +x scripts/setup-unix.sh
./scripts/setup-unix.sh my-project
# Restart shell, then run with full Phase 1-3 pipeline:
python scripts/opencode_runner.py my-project
```

### Phase Pipeline (Runs Automatically)
1. **Phase 1**: Verifies Node.js, OpenCode, API key, config, memory structure
2. **Phase 2**: Loads global/project memory, limitations, builds system prompt
3. **Phase 3**: Dual-verification: every response checked twice before output
4. **OpenCode**: Launches with full context active

## Phase System: 3-Stage Robustness Pipeline

Every OpenCode session runs through three mandatory phases:

| Phase | Script | Purpose |
|-------|--------|---------|
| **1. Verify** | `scripts/phase1_verify.py` | Confirms Node.js, OpenCode, API key, config, project structure |
| **2. Activate** | `scripts/phase2_activate.py` | Loads all memory, builds system prompt, writes activation files |
| **3. Verify** | `scripts/phase3_verify.py` | Dual-pass verification on every response (hallucination, scope, facts, safety, format) |

**Runner:** `scripts/opencode_runner.py` (or `scripts/opencode_runner.ps1` on Windows)

```bash
# Full pipeline
python scripts/opencode_runner.py my-project

# Skip Phase 1 (already verified)
python scripts/opencode_runner.py my-project --skip-phase1

# Test verification only (don't launch OpenCode)
python scripts/opencode_runner.py my-project --verify-only

# Initialize new project and run
python scripts/opencode_runner.py new-project --init
```

**Verification Details:**
- **Pass 1:** Hallucination check, scope compliance, factual consistency, code safety, format compliance
- **Pass 2:** Stricter thresholds + consistency with Pass 1
- **Result:** Both passes must approve for response to output
- **Logs:** Stored in `projects/<name>/cache/verification_*.json`

See `docs/PHASE_SYSTEM.md` for complete documentation.

| Feature | Description |
|---------|-------------|
| **Free API** | Uses NVIDIA's build.nvidia.com free tier (no GPU, no credit card) |
| **Memory System** | Global + per-project persistent memory (`memory/`, `projects/`) |
| **Cache** | Semantic cache with TTL (`cache/global/`, `cache/projects/`) |
| **Project Isolation** | Each project gets own input/output/cache/memory folders |
| **Rate Limiting** | Token-bucket per user/project (`scripts/rate_limiter.py`) |
| **Monitoring** | Prometheus + Grafana dashboards (`docker-compose.yml`) |
| **Self-Host Option** | vLLM / SGLang / TRT-LLM configs for 4×B200 or 8×H100 |
| **API Gateway** | Kong with auth, rate limits, circuit breaker (`gateway/kong.yml`) |
| **UI Docs** | Interactive website with screenshots (`website/index.html`) |

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Your PC    │────▶│  NVIDIA Free API │────▶│  Nemotron 3 Ultra   │
│  (OpenCode) │     │  (build.nvidia)  │     │  550B / 55B Active  │
└─────────────┘     └──────────────────┘     └─────────────────────┘
       │                                        │
       ▼                                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Local Infrastructure                      │
│  memory/global/MEMORY.md   projects/<name>/MEMORY.md        │
│  cache/global/             cache/projects/<name>/           │
│  scripts/rate_limiter.py   docker-compose.yml (self-host)   │
└─────────────────────────────────────────────────────────────┘
```

## Repository Structure

```
nemotron-3-ultra/
├── memory/
│   └── global/MEMORY.md          # Shared knowledge across all projects
├── cache/
│   ├── global/                   # Shared cache entries
│   └── projects/<name>/          # Per-project cache
├── projects/
│   └── <name>/
│       ├── MEMORY.md             # Project-specific memory
│       ├── input/                # Your input files
│       ├── output/               # Generated outputs
│       └── cache/                # Project cache + verification logs
├── scripts/
│   ├── memory_manager.py         # Memory/cache CLI
│   ├── rate_limiter.py           # Production rate limiting
│   ├── setup-windows.ps1         # Windows automated setup
│   ├── setup-unix.sh             # macOS/Linux automated setup
│   ├── phase1_verify.py          # Phase 1: Setup verification
│   ├── phase2_activate.py        # Phase 2: Memory/prompt activation
│   ├── phase3_verify.py          # Phase 3: Dual-verification
│   └── opencode_runner.py        # Main runner (runs all phases)
├── docs/
│   ├── PHASE_SYSTEM.md           # Phase system documentation
│   ├── 00-limitations.md         # Official model limits from NVIDIA
│   ├── 01-requirements.md
│   ├── 02-install-opencode.md
│   ├── 03-get-nvidia-api-key.md
│   ├── 04-configure-opencode.md
│   ├── 05-troubleshooting.md
│   └── 06-security-and-costs.md
├── examples/
│   └── opencode.example.json     # Config template
├── gateway/
│   └── kong.yml                  # API Gateway config
├── monitoring/
│   ├── prometheus.yml            # Prometheus scrape config
│   ├── datasources/datasources.yml
│   └── dashboards/nemotron-dashboard.json
├── docker-compose.yml            # Self-hosted deployment
├── website/
│   └── index.html                # Interactive docs with screenshots
├── README.md                     # This file
├── LICENSE
├── CONTRIBUTING.md
└── .gitignore
```

## Memory & Cache Usage

```bash
# Initialize a new project
python scripts/memory_manager.py init my-app "My application project"

# List all projects
python scripts/memory_manager.py list

# Show system status
python scripts/memory_manager.py status

# Sync global memory (git pull)
python scripts/memory_manager.py sync
```

## Free Tier Limitations

| Limit | Value |
|-------|-------|
| **Rate** | ~10-20 req/min, ~50k-100k tokens/min (unpublished) |
| **Daily quota** | Unpublished. Resets on 429. |
| **Context** | Up to 1M tokens (API may enforce lower) |
| **Concurrency** | Single-digit typically |
| **No SLA** | Can be throttled/disabled anytime |
| **Logging** | NVIDIA logs usage for security |

**For millions of users**: Self-host on 4× B200 (~$12-16/hr) or 8× H100 (~$24-32/hr). See `docker-compose.yml` and `docs/00-limitations.md`.

## Adding UI Screenshots

Place your HD screenshots (with blurred sensitive info) in:

```
website/assets/images/
├── step3-api-key.png          # NVIDIA API key generation
├── step5-opencode-running.png # OpenCode terminal with Nemotron
└── ...                        # Add more as needed
```

The website (`website/index.html`) has placeholder `<img>` tags ready.

## Self-Hosted Deployment (Production)

```bash
# 1. Download Nemotron 3 Ultra NVFP4 checkpoint
#    From Hugging Face: nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4

# 2. Set model path
export MODEL_PATH=/path/to/nemotron-3-ultra

# 3. Deploy with vLLM (recommended)
docker-compose up -d nemotron-vllm

# 4. Or deploy with SGLang (often faster)
docker-compose --profile sglang up -d nemotron-sglang

# 5. Full stack with gateway + monitoring
docker-compose up -d
```

## Security

- API keys **never stored in config files**: uses `{env:NVIDIA_API_KEY}`
- Set via `setx` (Windows) or shell RC (macOS/Linux)
- Rotate keys monthly or on 429 errors
- Free tier: NVIDIA logs usage. Don't send confidential data.

## Troubleshooting

| Error | Fix |
|-------|-----|
| `401 Unauthorized` | Regenerate API key at build.nvidia.com |
| `429 Rate Limited` | Wait 60s, reduce concurrency, check `scripts/rate_limiter.py` |
| Context exceeded | Reduce input, enable chunked prefill |
| Reasoning loops | Set `reasoning_budget: 512` in config |
| Tool call failures | Add `force_nonempty_content: true` |

See `docs/05-troubleshooting.md` for full guide.

## License

MIT. See `LICENSE`.

## Disclaimer

Not affiliated with NVIDIA or OpenCode. Free tier terms, limits, and model IDs can change. Always check build.nvidia.com for current details.