$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".tools\python\python.exe"
$pipScripts = Join-Path $root ".tools\python\Scripts"

if (Test-Path $python) {
    $env:PATH = "$pipScripts;$root\.tools\python;$env:PATH"
}

Set-Location (Join-Path $root "backend")

$port = if ($args[0]) { $args[0] } else { "8000" }

# If default port is busy, try 8001
if ($port -eq "8000") {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health/" -UseBasicParsing -TimeoutSec 2
        if ($r.Content -notmatch "track-log-api") {
            Write-Host "Port 8000 is in use by another app. Starting Track Log on 8001 instead."
            Write-Host "Update frontend/vite.config.js proxy target to http://127.0.0.1:8001 if needed."
            $port = "8001"
        }
    } catch { }
}

Write-Host "Starting Django on http://127.0.0.1:$port"
python manage.py runserver $port
