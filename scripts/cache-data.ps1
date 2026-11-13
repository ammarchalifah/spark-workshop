# Pre-download NYC TLC datasets into data/cache/ (optional; notebooks can download at runtime).
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

New-Item -ItemType Directory -Force -Path "data/cache" | Out-Null

$Base = "https://d37ci6vzurychx.cloudfront.net"

Write-Host "Downloading NYC TLC datasets into data/cache/ ..."

Invoke-WebRequest -Uri "$Base/trip-data/yellow_tripdata_2024-01.parquet" `
  -OutFile "data/cache/yellow_tripdata_2024-01.parquet"
Invoke-WebRequest -Uri "$Base/trip-data/yellow_tripdata_2024-02.parquet" `
  -OutFile "data/cache/yellow_tripdata_2024-02.parquet"
Invoke-WebRequest -Uri "$Base/misc/taxi_zone_lookup.csv" `
  -OutFile "data/cache/taxi_zone_lookup.csv"

Write-Host "Done. Cached files are under data/cache/"
