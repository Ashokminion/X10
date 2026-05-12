@echo off
echo Starting AI Workforce Platform...
echo.

REM Change to project root
cd /d "%~dp0"

echo [1/3] Starting AI Service (FastAPI on port 8000)...
start "AI Service" cmd /k "cd ai-service && python main.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend (React on port 3000)...
start "Frontend" cmd /k "cd frontend && npm start"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Backend (Spring Boot on port 8080)...
start "Backend" cmd /k "cd backend && mvn spring-boot:run -DskipTests"

echo.
echo ===============================================
echo Services are starting in separate windows...
echo ===============================================
echo.
echo Please wait 30-60 seconds for all services to initialize.
echo Then access: http://localhost:3000
echo.
echo Login credentials:
echo   Username: admin
echo   Password: admin123
echo.
pause
