$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Starting Backend Service ===" -ForegroundColor Cyan
Write-Host "Checking for Maven..." -ForegroundColor Yellow

# Use scoop shim path explicitly just in case PATH isn't updated in this session
$mvnPath = "$env:USERPROFILE\scoop\shims\mvn.cmd"
if (-not (Test-Path $mvnPath)) {
    $mvnPath = "mvn"
}

$bePath = Join-Path $root "backend"
$beCmd  = "Push-Location -LiteralPath '$bePath'; & '$mvnPath' spring-boot:run -DskipTests"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $beCmd
Write-Host "Backend starting in a new window..." -ForegroundColor Green
