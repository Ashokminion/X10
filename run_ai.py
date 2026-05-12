import os
import subprocess
import time

base_dir = r"d:\MEDIA\Audio studio ]\MINION\AK_AI-Based Shift Optimization System for Blue-Collar Workforce"
ai_service_dir = os.path.join(base_dir, "ai-service")

print(f"Changing directory to: {ai_service_dir}")
os.chdir(ai_service_dir)

print("Starting FastAPI AI Service...")
# Use absolute path to python and main.py
cmd = ["python", "main.py"]
subprocess.Popen(cmd)

print("AI Service started in background.")
time.sleep(5)
