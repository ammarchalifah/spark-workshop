# Spark Workshop Setup (Windows)
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

Write-Host "=== Spark Workshop Setup (Windows) ==="

# Check Java
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "Java: $javaVersion"
} catch {
    Write-Host "Java not found. Install with: winget install EclipseAdoptium.Temurin.17.JDK"
    exit 1
}

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "Docker: $dockerVersion"
} catch {
    Write-Host "Docker not found. Install Docker Desktop: https://docs.docker.com/desktop/setup/install/windows-install/"
    exit 1
}

# Python venv
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements/requirements.txt

Write-Host ""
Write-Host "Setup complete!"
Write-Host "  make cache-data   # optional: pre-download datasets (use WSL or Git Bash)"
Write-Host "  make up           # start Docker cluster"
Write-Host "  Open http://localhost:8888 in your browser"
