# basic.py
import os
import sys

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
backend_dir = os.path.join(ROOT_DIR, "backend")
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
