@echo off
set BASE_DIR="d:\MEDIA\Audio studio ]\MINION\AK_AI-Based Shift Optimization System for Blue-Collar Workforce"
echo Starting WorkforceAI System...

:: Start AI Service
echo [1/2] Starting AI Service (Port 8000)...
start "AI-Service" /D %BASE_DIR%\ai-service cmd /c "python main.py"

:: Start Frontend
echo [2/2] Starting Frontend (Port 3000)...
start "Frontend" /D %BASE_DIR%\frontend cmd /c "npm start"

echo.
echo System launched! 
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
pause
