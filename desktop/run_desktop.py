import os
import sys
import time
import subprocess
import signal
import httpx

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
FRONTEND_DIR = os.path.join(WORKSPACE_DIR, "frontend")
PYTHON_EXEC = os.path.join(BACKEND_DIR, "venv", "Scripts", "python.exe")

def is_service_ready(url: str, timeout: float = 1.0) -> bool:
    try:
        r = httpx.get(url, timeout=timeout)
        return r.status_code < 500
    except Exception:
        return False

def start_backend():
    print("[Desktop Launcher] Starting local FastAPI backend...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"
    cmd = [PYTHON_EXEC, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    return subprocess.Popen(
        cmd,
        cwd=WORKSPACE_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def start_frontend():
    print("[Desktop Launcher] Starting local Next.js frontend...")
    # Use production server if built, else dev
    cmd = ["npm.cmd", "run", "start"] if os.path.exists(os.path.join(FRONTEND_DIR, ".next")) else ["npm.cmd", "run", "dev"]
    return subprocess.Popen(
        cmd,
        cwd=FRONTEND_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True
    )

def launch_desktop():
    print("=" * 60)
    print("   ExamForge AI — Desktop Software Launcher (Offline Mode)")
    print("=" * 60)

    backend_proc = None
    frontend_proc = None

    try:
        # Check backend
        if not is_service_ready("http://127.0.0.1:8000/api/health"):
            backend_proc = start_backend()
        
        # Check frontend
        if not is_service_ready("http://localhost:3000"):
            frontend_proc = start_frontend()

        # Wait for both services
        print("[Desktop Launcher] Waiting for local services to initialize...")
        for i in range(40):
            b_ok = is_service_ready("http://127.0.0.1:8000/api/health")
            f_ok = is_service_ready("http://localhost:3000")
            if b_ok and f_ok:
                print("[Desktop Launcher] Local offline services ready!")
                break
            time.sleep(1)
        else:
            print("[Desktop Launcher] Notice: Starting desktop window (services still initializing)...")

        # Launch window using pywebview
        try:
            import webview
            print("[Desktop Launcher] Launching Native Desktop Window...")
            window = webview.create_window(
                title="ExamForge AI — Bilingual Examination Paper Generator",
                url="http://localhost:3000",
                width=1280,
                height=850,
                min_size=(1000, 680),
                confirm_close=False,
            )
            webview.start(debug=False)
        except Exception as e:
            print(f"[Desktop Launcher] PyWebView GUI mode fallback: {e}")
            # Fallback to Edge/Chrome App Mode (native borderless window)
            edge_paths = [
                os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            ]
            browser_bin = None
            for p in edge_paths:
                if os.path.exists(p):
                    browser_bin = p
                    break

            if browser_bin:
                print(f"[Desktop Launcher] Launching Windows Desktop App Window via {os.path.basename(browser_bin)}...")
                app_proc = subprocess.Popen([browser_bin, "--app=http://localhost:3000", "--window-size=1280,850"])
                app_proc.wait()
            else:
                import webbrowser
                webbrowser.open("http://localhost:3000")

    finally:
        print("[Desktop Launcher] Shutting down background services...")
        if backend_proc:
            try:
                backend_proc.terminate()
            except Exception:
                pass
        if frontend_proc:
            try:
                frontend_proc.terminate()
            except Exception:
                pass
        print("[Desktop Launcher] Closed cleanly.")

if __name__ == "__main__":
    launch_desktop()
