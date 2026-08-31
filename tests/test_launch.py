"""Basic smoke test verifying that the app starts up without errors."""

import os
import subprocess
import sys
import time
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / "app"

# How long to let the app run before we consider it "launched successfully".
STARTUP_GRACE_SECONDS = 3


def test_app_launches_without_errors():
    """Launch the app in a subprocess and check that it starts up cleanly.

    The app has no natural exit point (it's a GUI event loop), so once we've
    established that it started without crashing, it is forcibly terminated.
    """
    env = os.environ.copy()
    # Run headless so the test works without a display, e.g. in CI.
    env.setdefault("QT_QPA_PLATFORM", "offscreen")

    process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=APP_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        time.sleep(STARTUP_GRACE_SECONDS)

        if process.poll() is not None:
            output = process.stdout.read()
            raise AssertionError(
                f"App exited early with code {process.returncode}:\n{output}"
            )
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
