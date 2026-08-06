import os
import sys
import subprocess
import time

def main():
    print("=" * 60)
    print(" Launching HiLancer AI-Powered Freelancing Platform ")
    print("=" * 60)

    # Add project root to sys.path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    # Step 1: Initialize & Seed Database (8,000+ Jobs)
    print("\n[1/3] Initializing Database & Synthetic Jobs Dataset...")
    try:
        from backend.database.seed import seed_data
        seed_data(num_jobs=8000)
    except Exception as e:
        print(f"Seed note: {e}")

    # Step 2: Start FastAPI AI Microservice in background
    print("\n[2/3] Starting FastAPI AI Microservice on http://127.0.0.1:8000 ...")
    fastapi_proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "backend.ml_api.main:app", "--host", "127.0.0.1", "--port", "8000"
    ], cwd=project_root)

    time.sleep(3)

    # Step 3: Start Flask Web App
    print("\n[3/3] Starting Flask Web Server on http://127.0.0.1:5000 ...")
    print("\n Platform operational! Access the website in your browser at: http://127.0.0.1:5000")
    print("Press Ctrl+C to terminate services.\n")

    try:
        from backend.app.app import app
        app.run(host="127.0.0.1", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        fastapi_proc.terminate()

if __name__ == "__main__":
    main()
