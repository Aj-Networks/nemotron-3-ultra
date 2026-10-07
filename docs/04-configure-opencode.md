# 4. Configure OpenCode

## Config file location

| OS | Path |
|----|------|
| Windows | `%USERPROFILE%\.config\opencode\opencode.json` |
| macOS / Linux | `~/.config/opencode/opencode.json` |

## Config contents

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "nvidia/nvidia/nemotron-3-ultra-550b-a55b",
  "provider": {
    "nvidia": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "NVIDIA",
      "options": {
        "baseURL": "https://integrate.api.nvidia.com/v1",
        "apiKey": "{env:NVIDIA_API_KEY}"
      },
      "models": {
        "nvidia/nemotron-3-ultra-550b-a55b": {
          "name": "Nemotron 3 Ultra"
        }
      }
    }
  }
}
```

The config reads your key from the `NVIDIA_API_KEY` environment variable, so the key itself is never stored in the file.

## Create it (Windows PowerShell)

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\opencode" | Out-Null
@'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "nvidia/nvidia/nemotron-3-ultra-550b-a55b",
  "provider": {
    "nvidia": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "NVIDIA",
      "options": {
        "baseURL": "https://integrate.api.nvidia.com/v1",
        "apiKey": "{env:NVIDIA_API_KEY}"
      },
      "models": {
        "nvidia/nemotron-3-ultra-550b-a55b": {
          "name": "Nemotron 3 Ultra"
        }
      }
    }
  }
}
'@ | Set-Content -Encoding utf8 "$env:USERPROFILE\.config\opencode\opencode.json"
```

## Create it (macOS / Linux)

```bash
mkdir -p ~/.config/opencode
nano ~/.config/opencode/opencode.json
```

Paste the config contents above, save, and exit.

## Run it

```powershell
cd C:\path\to\your\project
opencode
```

1. Type `/models` and select **Nemotron 3 Ultra** (NVIDIA).
2. Type `hello` to test.

## Build vs Plan mode

- **Build** (default): can create and edit files in the current folder.
- **Plan**: read-only. Press **Tab** to switch.

Always launch OpenCode from a project folder, not your home directory.
