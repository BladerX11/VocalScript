import subprocess
import sys
from os import environ
from pathlib import Path
from subprocess import CalledProcessError

import tomllib
from tomllib import TOMLDecodeError

try:
    with (Path(__file__).parent.parent / "pyproject.toml").open("rb") as f:
        project_info = tomllib.load(f)

    version = str(project_info["project"]["version"])
    name = str(project_info["project"]["name"])
except (FileNotFoundError, TOMLDecodeError) as e:
    print(f"Error reading pyproject.toml: {e}", file=sys.stderr)
    sys.exit(1)

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
    f"--output-filename={name}",
    "--include-package=azure.cognitiveservices.speech",
    "--include-data-dir=resources=resources",
    "src/main.py",
]

if environ.get("CI") == "true":
    command.append("--assume-yes-for-downloads")

try:
    _ = subprocess.run(
        command,
        check=True,
    )
except CalledProcessError as e:
    sys.exit(e.returncode)
