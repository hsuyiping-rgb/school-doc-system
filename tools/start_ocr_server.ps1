$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "Starting local OCR service: http://localhost:8766"
Write-Host "Stop service: close this window or press Ctrl+C"
python tools/local_ocr_server.py
