$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d

Write-Host ""
Write-Host "Cluster starting."
Write-Host "  Jupyter Lab:  http://localhost:8888"
Write-Host "  Spark Master: http://localhost:8080"
Write-Host "  Spark App UI: http://localhost:4040 (after running a notebook)"
Write-Host ""
Write-Host "Follow logs: docker compose -f docker/docker-compose.yml logs -f"
