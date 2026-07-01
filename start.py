import subprocess
import sys
import os

def main():
    print("Starting FastAPI Backend...")
    # Start FastAPI
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    print("Starting Streamlit Frontend...")
    # Start Streamlit
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\nShutting down services...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
