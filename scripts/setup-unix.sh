#!/usr/bin/env bash
# Nemotron 3 Ultra + OpenCode Setup (macOS/Linux)
# Run: chmod +x setup-unix.sh && ./setup-unix.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_NAME="${1:-default}"
API_KEY="${2:-}"

echo "=== Nemotron 3 Ultra + OpenCode Setup (macOS/Linux) ==="

# 1. Check Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Install from https://nodejs.org (LTS) or via package manager."
    echo "  macOS: brew install node"
    echo "  Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
    exit 1
fi

NODE_VER=$(node --version)
echo "Node.js: $NODE_VER"
if [[ ! "$NODE_VER" =~ ^v(2[0-9]|[3-9][0-9]) ]]; then
    echo "Warning: Node.js 20+ recommended. Current: $NODE_VER"
fi

# 2. Install OpenCode
echo "Installing OpenCode..."
npm install -g opencode-ai
echo "OpenCode installed"

# Verify OpenCode installation
if command -v opencode &> /dev/null; then
    OC_VER=$(opencode --version)
    echo "OpenCode verified: $OC_VER"
else
    echo "Error: OpenCode installed but not in PATH. Restart shell and try again."
    exit 1
fi

# 3. Get API Key
if [[ -z "$API_KEY" ]]; then
    echo ""
    echo "Enter your NVIDIA API key (from https://build.nvidia.com):"
    echo "Format: nvapi-xxxxxxxxxxxx"
    read -s API_KEY
    echo ""
fi

if [[ ! "$API_KEY" =~ ^nvapi- ]] || [[ ${#API_KEY} -lt 45 ]]; then
    echo "Error: Invalid API key format. Must start with 'nvapi-' and be 45+ chars."
    exit 1
fi

# 4. Set environment variable
echo "Setting NVIDIA_API_KEY..."
export NVIDIA_API_KEY="$API_KEY"

# Persist to shell config
SHELL_CONFIG=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

if [[ -n "$SHELL_CONFIG" ]]; then
    if ! grep -q "NVIDIA_API_KEY" "$SHELL_CONFIG"; then
        echo 'export NVIDIA_API_KEY="'"$API_KEY"'"' >> "$SHELL_CONFIG"
        echo "Added to $SHELL_CONFIG"
    else
        echo "NVIDIA_API_KEY already in $SHELL_CONFIG"
    fi
fi

# 5. Write OpenCode config
CONFIG_DIR="$HOME/.config/opencode"
CONFIG_FILE="$CONFIG_DIR/opencode.json"

mkdir -p "$CONFIG_DIR"

if [[ -f "$CONFIG_FILE" ]]; then
    echo "Config exists at $CONFIG_FILE. Backing up and overwriting."
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%s)"
fi

cat > "$CONFIG_FILE" << 'EOF'
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
  },
  "agent": {
    "build": {
      "temperature": 1.0,
      "top_p": 0.95,
      "max_tokens": 32000
    },
    "plan": {
      "temperature": 1.0,
      "top_p": 0.95,
      "max_tokens": 32000
    }
  }
}
EOF

echo "Config written to $CONFIG_FILE"

# 6. Initialize memory/cache structure
if [[ -d "$REPO_ROOT" ]]; then
    echo "Initializing memory/cache structure..."
    python3 "$REPO_ROOT/scripts/memory_manager.py" init "$PROJECT_NAME" "Unix setup project"
    echo "Project '$PROJECT_NAME' initialized"
fi

# 7. Test run
echo ""
echo "=== Setup Complete ==="
echo "Next steps:"
echo "  1. Restart your shell (or run: source $SHELL_CONFIG)"
echo "  2. cd to your project folder"
echo "  3. Run: opencode"
echo "  4. Type '/models' and select 'Nemotron 3 Ultra (NVIDIA)'"
echo "  5. Type 'hello' to test"
echo ""
echo "Config location: $CONFIG_FILE"
echo "Memory location: $REPO_ROOT/memory/global/MEMORY.md"
echo "Project folder: $REPO_ROOT/projects/$PROJECT_NAME"