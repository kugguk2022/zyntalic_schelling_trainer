import uvicorn
import threading
import time
import sys
import os
import webbrowser

# Add project root to path so we can import zyntalic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps.web.app import app

PORT = 8001
HOST = "0.0.0.0"

def start_server():
    print(f"Starting server on {HOST}:{PORT}...")
    try:
        uvicorn.run(app, host=HOST, port=PORT, log_level="info")
    except Exception as e:
        print(f"CRITICAL SERVER ERROR: {e}")


def start_desktop():
    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    # Wait a bit for the server to start
    time.sleep(1)

    # Use localhost for the browser, even if we bind to 0.0.0.0 (all interfaces)
    browser_url = f"http://127.0.0.1:{PORT}"
    print(f"Opening Zyntalic at {browser_url}")

    try:
        import webview
        # Check for start() failure specifically
        webview.create_window("Zyntalic Translator", browser_url, width=1024, height=768)
        webview.start()
    except Exception as e:
        print(f"pywebview failed to start ({e}). Falling back to system browser.")
        
        # WSL specific handling: xdg-open often fails, so use Windows tools
        import platform
        is_wsl = "microsoft" in platform.uname().release.lower()
        
        if is_wsl:
            try:
                # specific to WSL -> Windows bridge
                print("WSL detected: Attempting to open via explorer.exe")
                os.system(f"explorer.exe {browser_url}")
            except Exception:
                webbrowser.open(browser_url)
        else:
            webbrowser.open(browser_url)
        
        # Keep the main thread alive if we're not using webview's blocking loop
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")

if __name__ == "__main__":
    start_desktop()
