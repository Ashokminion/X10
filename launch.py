import subprocess
import os
import sys
import time

def launch():
    base_dir = r"d:\MEDIA\Audio studio ]\MINION\AK_AI-Based Shift Optimization System for Blue-Collar Workforce"
    ai_dir = os.path.join(base_dir, "ai-service")
    frontend_dir = os.path.join(base_dir, "frontend")

    print(f"Launching from: {base_dir}")

    # Start AI Backend
    print("Starting AI Backend...")
    # We use shell=True and absolute path to main.py
    # We also try to set CWD in the subprocess call
    backend_proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=ai_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

    # Start Frontend
    print("Starting Frontend...")
    frontend_proc = subprocess.Popen(
        ["npm.cmd", "start"], # npm.cmd is needed on Windows for Popen without shell=True
        cwd=frontend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

    print("\nProcesses launched in new windows.")
    print("AI Backend: http://localhost:8000")
    print("Frontend: http://localhost:3000")
    
    # Keep the parent alive for a moment
    time.sleep(5)

if __name__ == "__main__":
    launch()
