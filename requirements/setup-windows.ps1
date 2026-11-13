# Preflight: Docker only (Java, Python, PySpark, Jupyter live in the cluster image).
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

Write-Host "=== Spark lab preflight (Windows) ==="

try {
    $dockerVersion = docker --version
    Write-Host "Docker: $dockerVersion"
} catch {
    Write-Host "Docker not found. Install Docker Desktop (WSL2 backend):"
    Write-Host "  https://docs.docker.com/desktop/setup/install/windows-install/"
    exit 1
}

try {
    docker compose version | Write-Host
} catch {
    Write-Host "Docker Compose not available. Update Docker Desktop."
    exit 1
}

Write-Host ""
Write-Host "Next steps:"
Write-Host "  .\scripts\cluster-up.ps1   # build image and start cluster"
Write-Host "  Open http://localhost:8888 in your browser"
