# Gemini RAG 실행 스크립트 (PowerShell)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "===== Gemini RAG 실행 =====" -ForegroundColor Cyan

if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "[uv 감지] uv로 실행합니다..." -ForegroundColor Green
    uv run --with google-genai python main.py
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "[Python 감지] python으로 실행합니다..." -ForegroundColor Green
    Write-Host "google-genai 패키지가 필요합니다: pip install google-genai" -ForegroundColor Yellow
    python main.py
} else {
    Write-Host "[!] Python이 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "    https://www.python.org/downloads/ 에서 설치하세요."
    Write-Host '    또는 uv를 설치하세요: irm https://astral.sh/uv/install.ps1 | iex'
}

Read-Host "Enter를 누르면 종료됩니다"
