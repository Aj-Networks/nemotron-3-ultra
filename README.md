# Nemotron 3 Ultra + OpenCode

Run NVIDIA's **Nemotron 3 Ultra (550B)** as a coding assistant in your terminal. Free API, no GPU, no credit card.

**Try it and [share your thoughts](https://github.com/Aj-Networks/nemotron-3-ultra/issues).**

**[Open the step-by-step guide](https://aj-networks.github.io/nemotron-3-ultra/)** for a visual walkthrough.

## Quick start

You need: [Node.js LTS](https://nodejs.org), Python 3, and a free key from [build.nvidia.com](https://build.nvidia.com).

**Windows (PowerShell)**
```powershell
git clone https://github.com/Aj-Networks/nemotron-3-ultra.git
cd nemotron-3-ultra
.\scripts\setup-windows.ps1 -ProjectName my-project
# reopen PowerShell, then:
python scripts/opencode_runner.py my-project
```

**macOS / Linux**
```bash
git clone https://github.com/Aj-Networks/nemotron-3-ultra.git
cd nemotron-3-ultra
./scripts/setup-unix.sh my-project
# restart shell, then:
python scripts/opencode_runner.py my-project
```

## What you get

- **Free model**: 550B params, up to 1M context, via NVIDIA's free tier
- **Memory**: global and per-project, kept between sessions
- **Checks**: setup verified before launch, replies checked twice
- **Rate limiting**: stays inside free-tier limits
- **Self-host option**: vLLM or SGLang, Kong gateway, Grafana dashboards (Docker)

## Docs

| Guide | |
|---|---|
| [Requirements](docs/01-requirements.md) | [Troubleshooting](docs/05-troubleshooting.md) |
| [Install OpenCode](docs/02-install-opencode.md) | [Limits](docs/00-limitations.md) |
| [Get API key](docs/03-get-nvidia-api-key.md) | [Security and costs](docs/06-security-and-costs.md) |
| [Configure](docs/04-configure-opencode.md) | [How the checks work](docs/PHASE_SYSTEM.md) |

## Good to know

- Free tier is roughly 10-20 requests/min with no SLA.
- NVIDIA logs free-tier usage. Don't send confidential code.
- Not affiliated with NVIDIA or OpenCode.

## Feedback

Bug, idea, or result to share? [Open an issue](https://github.com/Aj-Networks/nemotron-3-ultra/issues). PRs welcome, see [CONTRIBUTING](CONTRIBUTING.md).

MIT License
