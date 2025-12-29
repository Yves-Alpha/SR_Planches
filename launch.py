#!/usr/bin/env python3
import hashlib
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

# Forcer le PATH pour inclure Homebrew (Poppler)
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]

DEFAULT_PORT = 8501
base_path = Path(__file__).resolve().parent
venv_path = base_path / "venv"
venv_python = venv_path / "bin" / "python"
req_file = base_path / "requirements.txt"
req_hash_file = venv_path / ".req_hash"
app_path = base_path / "app" / "main.py"


def pick_python() -> Path:
    candidates = [
        Path("/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"),
        Path("/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"),
        Path("/opt/homebrew/bin/python3"),
        Path("/usr/local/bin/python3"),
    ]
    for c in candidates:
        if c.exists() and os.access(c, os.X_OK):
            return c
    from shutil import which

    w = which("python3")
    if w:
        return Path(w)
    print("Python 3 est introuvable. Installe Python 3.12 depuis python.org.")
    sys.exit(1)


def ensure_poppler():
    from shutil import which

    if which("pdftoppm"):
        return
    print("Poppler (pdftoppm) est introuvable. Installe-le via Homebrew : 'brew install poppler'.")


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_venv():
    python_bin = pick_python()
    need_install = not venv_python.exists()

    cur_hash = file_hash(req_file) if req_file.exists() else ""
    old_hash = req_hash_file.read_text().strip() if req_hash_file.exists() else ""
    if cur_hash and cur_hash != old_hash:
        need_install = True

    if need_install:
        print("Création/mise à jour du venv…")
        subprocess.run([str(python_bin), "-m", "venv", str(venv_path)], check=True)
        subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
        if req_file.exists():
            subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(req_file), "--disable-pip-version-check"], check=True)
            if cur_hash:
                req_hash_file.write_text(cur_hash)

    # Sanity check imports
    subprocess.run(
        [
            str(venv_python),
            "-c",
            "import streamlit, pikepdf, reportlab, PyPDF2, pdf2image, PIL, tkinter",
        ],
        check=True,
    )


def launch_app():
    subprocess.run(["pkill", "-f", "streamlit"], stderr=subprocess.DEVNULL)
    cmd = [
        str(venv_path / "bin" / "streamlit"),
        "run",
        str(app_path),
        f"--server.port={DEFAULT_PORT}",
        "--server.headless=false",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
    ]
    subprocess.Popen(cmd, cwd=str(base_path))


def wait_for_port(port: int, timeout: float = 30.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start = time.time()
    try:
        while True:
            result = sock.connect_ex(("localhost", port))
            if result == 0:
                return True
            if time.time() - start > timeout:
                return False
            time.sleep(0.1)
    finally:
        sock.close()


def main():
    ensure_poppler()
    ensure_venv()
    launch_app()
    if wait_for_port(DEFAULT_PORT):
        print(f"SR Planches lancé sur http://localhost:{DEFAULT_PORT}")
        print("Le navigateur devrait s’ouvrir automatiquement (géré par Streamlit).")
        print("Si rien ne s’ouvre, copie/colle cette URL dans ton navigateur.")
    else:
        print("Le serveur Streamlit n'a pas démarré dans le délai imparti.")
        sys.exit(1)


if __name__ == "__main__":
    main()
