import os
import threading
import time
import webview
import requests
import sys
from pathlib import Path
from django.core.management import execute_from_command_line

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tasktracker.settings")
# --- CONFIGURATION ---
DJANGO_PORT = 9000  # Changed to a less common port to avoid conflict
DJANGO_URL = f"http://127.0.0.1:{DJANGO_PORT}"
APP_NAME = "Task Tracker App"
TIMEOUT = 30 # Increased timeout for slow system start
# ---------------------

def get_bundled_path(relative_path):
    """
    Determines the correct absolute path for bundled resources.
    Uses sys._MEIPASS when the application is bundled (frozen).
    """
    if getattr(sys, 'frozen', False):
        # App is running as a PyInstaller executable
        base_path = sys._MEIPASS
    else:
        # App is running as a script
        base_path = os.path.dirname(__file__)

    # PyInstaller puts files added via --add-data at the root of the bundle
    return os.path.join(base_path, relative_path)

def configure_django_environment():
    """
    Sets up Django's settings and environment variables necessary for running
    inside a PyInstaller bundle, primarily fixing the database path.
    """
    print("⚙️ Configuring bundled Django environment...")
    
    # 1. Update the database path environment variable (needed by settings.py)
    # NOTE: Your settings.py must be configured to read this environment variable
    # or you must directly import and modify 'django.conf.settings'.
    
    # Assuming your tasktracker/settings.py uses BASE_DIR to define the database path,
    # we must ensure that the environment variable used by Django is set correctly.
    # The simplest way is to ensure the database file is located correctly.
    
    # We'll rely on Django's setup to pull the path from settings, but we need
    # to make sure Django knows where the settings file is located.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tasktracker.settings'

    # Inject the database path fix directly into Django's configuration before setup.
    try:
        from django.conf import settings
        # This will raise an error if settings is not configured, so we wrap it.
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': get_bundled_path('db.sqlite3'),
                }
            },
            # Add other necessary settings here if they are missing (e.g., SECRET_KEY)
            SECRET_KEY='pyinstaller-secret-key-1234',
            ROOT_URLCONF='tasktracker.urls',
            ALLOWED_HOSTS=['127.0.0.1', 'localhost', '*'], # Allow local connections
            INSTALLED_APPS=[
                # Must list all required apps here if settings.configure is used
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'login',
                # Add any other custom apps like 'tasktracker' if applicable
            ],
            STATIC_URL='/static/',
            # Ensure the system knows we are running in a bundled context
            PYINSTALLER_BUNDLED = True 
        )
        import django
        django.setup()
        print(f"✅ Database path set to: {settings.DATABASES['default']['NAME']}")
    except Exception as e:
        # This catches errors if the settings file itself is not found/imported
        print(f"❌ Error configuring Django settings: {e}")
        # We allow it to continue, but the app might fail later
        pass


def start_django_internal():
    """
    Starts the Django server using the internal management utility.
    This replaces the unreliable subprocess call.
    """
    configure_django_environment()
    
    try:
        # We pass the command 'runserver' along with necessary flags
        execute_from_command_line([
            sys.argv[0],  # Dummy script name
            'runserver',
            '--noreload',   # Crucial: Prevents code reloading which fails in PyInstaller
            '--nothreading', # Important: Use built-in Python threading instead of Django's
            f"127.0.0.1:{DJANGO_PORT}"
        ])
    except Exception as e:
        print(f"❌ Django internal server startup failed: {e}")


def wait_for_server(url, timeout=TIMEOUT):
    """Wait until Django server starts responding."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # We check the base URL, not the login page, for readiness
            r = requests.get(url, timeout=1) 
            if r.status_code in [200, 302]: # Check for 200 (Success) or 302 (Redirect)
                return True
        except requests.exceptions.ConnectionError:
            pass
        except Exception:
            pass
        time.sleep(0.5)
    return False

def main():
    print("🚀 Starting Django server...")
    # Start the Django server in a background thread
    threading.Thread(target=start_django_internal, daemon=True).start()

    # Wait until Django is ready
    if not wait_for_server(DJANGO_URL):
        print("Could not start Django. Exiting.")
        return

    print("🪟 Launching desktop window...")
    webview.create_window(
        APP_NAME,
        f"{DJANGO_URL}/login",
        width=1200,
        height=800,
        resizable=True,
    )
    # webview.start() is blocking, so the Django thread runs until the window closes.
    webview.start()

if __name__ == "__main__":
    main()