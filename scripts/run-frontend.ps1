$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$node = Join-Path $root ".tools\node\node.exe"

if (Test-Path $node) {
    $env:PATH = "$root\.tools\node;$env:PATH"
}

Set-Location (Join-Path $root "frontend")

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..."
    npm install
}

Write-Host "Starting Vite on http://localhost:5173"
npm run dev
