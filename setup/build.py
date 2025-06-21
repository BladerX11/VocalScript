import os
import subprocess
import sys

version = "0.1"
command = [
    sys.executable,
    "-m",
    "nuitka",
    "--mode=app",
    f"--product-version={version}",
    "--windows-console-mode=disable",
    f"--macos-app-version={version}",
    "--enable-plugin=pyside6",
    "--output-dir=dist",
    "--output-filename=vocalscript",
    "--include-package=azure.cognitiveservices.speech",
    "--include-data-dir=resources=resources",
    "src/main.py",
]

if sys.platform == "win32" and os.environ.get("CI") == "true":
    command.append("--assume-yes-for-downloads")

try:
    _ = subprocess.run(
        command,
        check=True,
    )
except subprocess.CalledProcessError as e:
    sys.exit(e.returncode)
