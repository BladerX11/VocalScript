import sys
from pathlib import Path

import PyInstaller.__main__
import tomllib
from tomllib import TOMLDecodeError

try:
    with (Path(__file__).parent.parent / "pyproject.toml").open("rb") as f:
        project_info = tomllib.load(f)

    name = str(project_info["project"]["name"])
except (FileNotFoundError, TOMLDecodeError) as e:
    print(f"Error reading pyproject.toml: {e}", file=sys.stderr)
    sys.exit(1)

command = [
    "--log-level=WARN",
    "vocalscript.spec",
    # after generating, add a.binaries = [b for b in a.binaries if not b[0].endswith("libstdc++.so.6")]
    # "src/main.py",
    # "-F",
    # "-w",
    # "-n=vocalscript",
    # f"--add-data=resources{';' if sys.platform == 'win32' else ':'}resources",
    # "--hidden-import=services.azure",
    # "--collect-binaries=azure.cognitiveservices.speech",
    # "--hidden-import=services.kokoro",
    # "--collect-data=language_tags",
    # "--collect-data=espeakng_loader",
    # "--collect-data=misaki",
    # "--collect-all=en_core_web_sm",
    # "--collect-all=en_core_web_trf",
    # "--hidden-import=services.chatterbox",
    # "--collect-data=perth",
    # "--hidden-import=sklearn._cyutility",
]

PyInstaller.__main__.run(command)
