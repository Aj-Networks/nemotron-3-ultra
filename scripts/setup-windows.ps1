<#>
.SYNOPSIS
    Complete setup for Nemotron 3 Ultra + OpenCode on Windows
.DESCRIPTION
    Installs Node.js (if missing), OpenCode, configures NVIDIA API key,
    writes OpenCode config, and initializes memory/cache structure.
.NOTES
    Run in PowerShell as Administrator for Node.js install (optional).
    For user-level install, run without admin.
#>

param(
    [string]$ApiKey = "",
    [string]$ProjectName = "default",
    [switch]$SkipNodeCheck,
    [switch]$ForceReconfigure
)

$ErrorActionPreference = "Stop"

Write-Host "=== Nemotron 3 Ultra + OpenCode Setup (Windows) ===" -ForegroundColor Cyan

# 1. Check Node.js
if (-not $SkipNodeCheck) {
    try {
        $nodeVer = node --version
        Write-Host "Node.js: $nodeVer" -ForegroundColor Green
        if ($nodeVer -notmatch '^v(2[0-9]|[3-9]\d)') {
            Write-Warning "Node.js 20+ recommended. Current: $nodeVer"
        }
    } catch {
        Write-Error "Node.js not found. Install from https://nodejs.org (LTS) and re-run."
        exit 1
    }
}

# 2. Install OpenCode
Write-Host "`nInstalling OpenCode..." -ForegroundColor Yellow
try {
    npm install -g opencode-ai
    Write-Host "OpenCode installed" -ForegroundColor Green
} catch {
    Write-Error "npm install failed. Check Node.js and npm."
    exit 1
}

# 3. Get API Key
if (-not $ApiKey) {
    Write-Host "`nEnter your NVIDIA API key (from https://build.nvidia.com):" -ForegroundColor Cyan
    Write-Host "Format: nvapi-xxxxxxxxxxxx" -ForegroundColor Gray
    $secureKey = Read-Host -AsSecureString
    $ApiKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    )
}

if (-not $ApiKey.StartsWith("nvapi-") -or $ApiKey.Length -lt 45) {
    Write-Error "Invalid API key format. Must start with 'nvapi-' and be 45+ chars."
    exit 1
}

# 4. Set environment variable (persistent + current session)
Write-Host "`nSetting NVIDIA_API_KEY..." -ForegroundColor Yellow
setx NVIDIA_API_KEY $ApiKey
$env:NVIDIA_API_KEY = $ApiKey
Write-Host "API key set (persistent + current session)" -ForegroundColor Green

# 5. Write OpenCode config
$configDir = "$env:USERPROFILE\.config\opencode"
$configFile = "$configDir\opencode.json"

if (Test-Path $configFile -and -not $ForceReconfigure) {
    Write-Host "`nConfig exists at $configFile. Use -ForceReconfigure to overwrite." -ForegroundColor Yellow
} else {
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null

    $config = @{
        '$schema' = 'https://opencode.ai/config.json'
        model = 'nvidia/nvidia/nemotron-3-ultra-550b-a55b'
        provider = @{
            nvidia = @{
                npm = '@ai-sdk/openai-compatible'
                name = 'NVIDIA'
                options = @{
                    baseURL = 'https://integrate.api.nvidia.com/v1'
                    apiKey = '{env:NVIDIA_API_KEY}'
                }
                models = @{
                    'nvidia/nemotron-3-ultra-550b-a55b' = @{
                        name = 'Nemotron 3 Ultra'
                    }
                }
            }
        }
        agent = @{
            build = @{
                temperature = 1.0
                top_p = 0.95
                max_tokens = 32000
            }
            plan = @{
                temperature = 1.0
                top_p = 0.95
                max_tokens = 32000
            }
        }
    }

    $config | ConvertTo-Json -Depth 10 | Set-Content -Encoding utf8 $configFile
    Write-Host "Config written to $configFile" -ForegroundColor Green
}

# 6. Initialize memory/cache structure
$repoRoot = "$env:USERPROFILE\OneDrive\AI\nemotron 3 ultra"
if (Test-Path $repoRoot) {
    Write-Host "`nInitializing memory/cache structure..." -ForegroundColor Yellow
    python "$repoRoot\scripts\memory_manager.py" init $ProjectName "Windows setup project"
    Write-Host "Project '$ProjectName' initialized" -ForegroundColor Green
}

# 7. Test run
Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "Next steps:"
Write-Host "  1. Close and reopen PowerShell (for setx to take effect)"
Write-Host "  2. cd to your project folder"
Write-Host "  3. Run: opencode"
Write-Host "  4. Type '/models' and select 'Nemotron 3 Ultra (NVIDIA)'"
Write-Host "  5. Type 'hello' to test"
Write-Host "`nConfig location: $configFile"
Write-Host "Memory location: $repoRoot\memory\global\MEMORY.md"
Write-Host "Project folder: $repoRoot\projects\$ProjectName"