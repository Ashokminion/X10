$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== AI Workforce Platform Launcher ===" -ForegroundColor Cyan

# --- Start AI Service ---
Write-Host "[1/3] Starting AI Service (FastAPI on port 8000)..." -ForegroundColor Yellow
$aiPath = Join-Path $root "ai-service"
$aiCmd  = "Push-Location -LiteralPath '$aiPath'; python main.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $aiCmd

Start-Sleep -Seconds 3

# --- Start Frontend ---
Write-Host "[2/3] Starting Frontend (React on port 3000)..." -ForegroundColor Yellow
$fePath = Join-Path $root "frontend"
$feCmd  = "Push-Location -LiteralPath '$fePath'; npm start"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $feCmd

Start-Sleep -Seconds 3

# --- Backend (requires Maven) ---
Write-Host "[3/3] Checking for Maven (backend)..." -ForegroundColor Yellow
$mvnCmd = Get-Command mvn -ErrorAction SilentlyContinue
if ($mvnCmd) {
    $bePath = Join-Path $root "backend"
    $beCmd  = "Push-Location -LiteralPath '$bePath'; mvn spring-boot:run -DskipTests"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $beCmd
    Write-Host "    Backend starting..." -ForegroundColor Green
} else {
    Write-Host "    [SKIP] Maven not found. Backend will not start." -ForegroundColor Red
    Write-Host "    Install Maven from https://maven.apache.org/download.cgi" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host " Frontend  -> http://localhost:3000" -ForegroundColor Green
Write-Host " AI API    -> http://localhost:8000/docs" -ForegroundColor Green
Write-Host " Login:       admin / admin123" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
