import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

# Add Backend and Database directories to sys.path
project_root = Path(__file__).resolve().parent
backend_dir = project_root / "Backend"
db_dir = project_root / "Database"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(db_dir) not in sys.path:
    sys.path.insert(0, str(db_dir))

from app import app

if __name__ == "__main__":
    print("Starting AI Preparation Portal on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)

