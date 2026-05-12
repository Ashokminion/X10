import os
import subprocess
import time
import sys

# Use relative paths from the script location to bypass path syntax issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.join(BASE_DIR, "ai-service")
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
MVN_PATH = os.path.join(BASE_DIR, "tmp_tools", "apache-maven-3.9.6", "bin", "mvn.cmd")

processes = []

def start_service(name, cwd, cmd):
    print(f"--- Starting {name} ---")
    print(f"CWD: {cwd}")
    print(f"Cmd: {cmd}")
    try:
        # Use shell=True for Maven/Npm on Windows as they are .cmd/.bat
        p = subprocess.Popen(cmd, cwd=cwd, shell=True)
        processes.append(p)
        return p
    except Exception as e:
        print(f"Failed to start {name}: {e}")
        return None

def main():
    # 1. Start AI Service
    # Using 'python' 'main.py' as a list
    start_service("AI Microservice (FastAPI)", AI_DIR, ["python", "main.py"])
    
    # 2. Start Frontend
    start_service("Frontend (React)", FRONTEND_DIR, ["npm", "start"])
    
    # 3. Start Backend
    # Use relative path to mvn
    backend_cmd = [MVN_PATH, "spring-boot:run", "-DskipTests"]
    start_service("Backend (Spring Boot)", BACKEND_DIR, backend_cmd)

    print("\n--- Processes launched ---")
    print("Wait for ports to open...")
    
    try:
        while True:
            time.sleep(2)
            # Check if processes are alive
            for p in processes:
                if p.poll() is not None:
                    print(f"Warning: A process exited with code {p.returncode}")
    except KeyboardInterrupt:
        print("\nTermination signal received.")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()
