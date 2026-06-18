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

$port = if ($args[0]) { $args[0] } else { "5173" }
$apiPort = if ($args[1]) { $args[1] } else { "8001" }

$env:VITE_PORT = $port
$env:VITE_API_TARGET = "http://127.0.0.1:$apiPort"

Write-Host "Starting Vite on http://localhost:$port (API proxy -> $env:VITE_API_TARGET)"
npm run dev
