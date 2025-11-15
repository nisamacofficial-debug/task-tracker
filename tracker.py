import subprocess
import time
import webview
import threading
import os


import sys, os

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

manage_py = os.path.join(BASE_DIR, "manage.py")


def run_server():
    # Start Django server
    subprocess.Popen(["python", "manage.py", "runserver", "8000"])

def open_app():
    # Wait for server to start
    time.sleep(3)
    webview.create_window("My Django App", "http://127.0.0.1:8000")
    webview.start()

if __name__ == '__main__':
    threading.Thread(target=run_server).start()
    open_app()