$ErrorActionPreference = "Stop"

Write-Host "Installing free OCR tools: Tesseract and Python PDF/OCR packages"
Write-Host "If Windows asks for permission, allow the installation."

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
  throw "winget was not found. Install App Installer first, or install Tesseract manually."
}

winget install --id UB-Mannheim.TesseractOCR -e --accept-package-agreements --accept-source-agreements

python -m pip install --upgrade pip
python -m pip install --upgrade pypdfium2

$tessdataDir = Join-Path $PSScriptRoot "tessdata"
New-Item -ItemType Directory -Force -Path $tessdataDir | Out-Null
$chiTra = Join-Path $tessdataDir "chi_tra.traineddata"
if (-not (Test-Path $chiTra)) {
  Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata_best/raw/main/chi_tra.traineddata" -OutFile $chiTra
}
$eng = Join-Path $tessdataDir "eng.traineddata"
if (-not (Test-Path $eng)) {
  Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata" -OutFile $eng
}

Write-Host ""
Write-Host "After installation, reopen PowerShell and run:"
Write-Host "  .\tools\start_ocr_server.ps1"
Write-Host ""
Write-Host "If Traditional Chinese OCR fails, confirm Tesseract has the chi_tra language pack."
