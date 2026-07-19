"""Desktop launcher for Stoichiometry Fitter.

Uses pywebview to open a native window with FastAPI serving on localhost.
"""

import os
import subprocess
import sys
import threading
import time

import webview

# Project root
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

BACKEND_PORT = 8000
BACKEND_URL = f'http://127.0.0.1:{BACKEND_PORT}'

def start_backend():
    """Start the FastAPI backend server."""
    import backend.app as app
    import uvicorn
    config = uvicorn.Config(app.app, port=BACKEND_PORT, log_level='info')
    server = uvicorn.Server(config)
    server.run()

def main():
    """Launch the desktop app."""
    # Start backend in a background thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    time.sleep(1.5)  # Let server start

    # Create webview window
    window = webview.create_window(
        'Stoichiometry Fitter',
        BACKEND_URL,
        width=1400,
        height=900,
    )
    webview.start()

if __name__ == '__main__':
    main()
