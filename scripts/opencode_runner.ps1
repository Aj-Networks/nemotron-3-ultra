<#>
.SYNOPSIS
    Run Nemotron 3 Ultra + OpenCode with full Phase 1-3 verification
.DESCRIPTION
    Executes the complete pipeline: Phase 1 (setup verify), Phase 2 (memory activate), Phase 3 (dual-verification), then launches OpenCode.
.PARAMETER ProjectName
    Project name (default: "default")
.PARAMETER SkipPhase1
    Skip Phase 1 setup verification
.PARAMETER VerifyOnly
    Run verification tests only, don't launch OpenCode
.PARAMETER Init
    Initialize project before running
.EXAMPLE
    .\scripts\opencode_runner.ps1 my-project
.EXAMPLE
    .\scripts\opencode_runner.ps1 default -SkipPhase1
.EXAMPLE
    .\scripts\opencode_runner.ps1 test-project -VerifyOnly -Init
#>

param(
    [string]$ProjectName = "default",
    [switch]$SkipPhase1,
    [switch]$VerifyOnly,
    [switch]$Init
)

$ErrorActionPreference = "Stop"

$repoRoot = "$env:USERPROFILE\OneDrive\AI\nemotron 3 ultra"
$scriptPath = "$repoRoot\scripts\opencode_runner.py"

if (-not (Test-Path $scriptPath)) {
    Write-Error "Runner script not found at $scriptPath"
    exit 1
}

# Build arguments
$args = @($ProjectName)
if ($SkipPhase1) { $args += "--skip-phase1" }
if ($VerifyOnly) { $args += "--verify-only" }
if ($Init) { $args += "--init" }

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "NEMOTRON 3 ULTRA + OPENCODE RUNNER" -ForegroundColor Cyan
Write-Host "Project: $ProjectName" -ForegroundColor Yellow
Write-Host "Args: $($args -join ' ')" -ForegroundColor Gray
Write-Host "=" * 60 -ForegroundColor Cyan

# Run
try {
    python $scriptPath @args
    $exitCode = $LASTEXITCODE
} catch {
    Write-Error "Runner failed: $_"
    exit 1
}

if ($exitCode -ne 0) {
    Write-Error "Runner exited with code $exitCode"
}

exit $exitCode