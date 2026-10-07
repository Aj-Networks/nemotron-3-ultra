# 2. Install OpenCode

OpenCode is a terminal coding assistant. It is only the interface; it does not include a model.

## Windows (PowerShell)

1. Install **Node.js LTS** from nodejs.org.
2. Open PowerShell and run:

```powershell
npm i -g opencode-ai
```

3. Verify:

```powershell
opencode --version
```

> The npm "new version available" notice is harmless. Ignore it.

## macOS / Linux / WSL

```bash
curl -fsSL https://opencode.ai/install | bash
```

Or with npm:

```bash
npm i -g opencode-ai
```

## Tip for Windows

If OpenCode behaves oddly in PowerShell, install WSL (`wsl --install`) and use the Linux installer inside it.
