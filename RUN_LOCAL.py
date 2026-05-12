import os
import subprocess
import time
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.join(BASE_DIR, "ai-service")
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
MVN_PATH = os.path.join(BASE_DIR, "tmp_tools", "apache-maven-3.9.6", "bin", "mvn.cmd")

def start_service(name, cwd, cmd, env=None):
    print(f"\n>>> Starting {name}...")
    my_env = os.environ.copy()
    if env:
        my_env.update(env)
    
    try:
        # Use shell=True for Windows commands (mvn.cmd, npm.cmd)
        p = subprocess.Popen(cmd, cwd=cwd, env=my_env, shell=True)
        return p
    except Exception as e:
        print(f"!!! Failed to start {name}: {e}")
        return None

def main():
    print("====================================================")
    print("        AI Workforce Intelligence Local Runner")
    print("====================================================\n")

    # 1. Initialize AI Service SQLite DB
    print(">>> Initializing AI Service (SQLite)...")
    try:
        subprocess.run([sys.executable, "init_sqlite.py"], cwd=AI_DIR, check=True, env={"DB_TYPE": "sqlite"})
    except Exception as e:
        print(f"!!! DB Initialization failed: {e}")
        print("Continuing anyway...")

    processes = []

    # 2. Start AI Service
    ai_proc = start_service(
        "AI Microservice (FastAPI)", 
        AI_DIR, 
        [sys.executable, "main.py"],
        env={"DB_TYPE": "sqlite", "SERVICE_PORT": "8000"}
    )
    if ai_proc: processes.append(ai_proc)

    # 3. Start Backend
    # Use the bundled maven
    backend_proc = start_service(
        "Backend (Spring Boot)", 
        BACKEND_DIR, 
        [MVN_PATH, "spring-boot:run", "-DskipTests"]
    )
    if backend_proc: processes.append(backend_proc)

    # 4. Start Frontend
    frontend_proc = start_service(
        "Frontend (React)", 
        FRONTEND_DIR, 
        ["npm", "start"]
    )
    if frontend_proc: processes.append(frontend_proc)

    print("\n----------------------------------------------------")
    print("All services are starting...")
    print("- Frontend: http://localhost:3000")
    print("- Backend:  http://localhost:8080")
    print("- AI Docs:   http://localhost:8000/docs")
    print("----------------------------------------------------")
    print("Press Ctrl+C to terminate all services.")

    try:
        while True:
            time.sleep(2)
            # Monitor processes
            for p in processes:
                if p.poll() is not None:
                    print(f"\n!!! Warning: A process exited with code {p.returncode}")
                    processes.remove(p)
    except KeyboardInterrupt:
        print("\n>>> Terminating all services...")
        for p in processes:
            p.terminate()
            p.wait()
        print("Done.")

if __name__ == "__main__":
    main()
