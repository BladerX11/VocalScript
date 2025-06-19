import PyInstaller.__main__

PyInstaller.__main__.run(
    [
        "src/main.py",
        "--onefile",
        "--windowed",
        "--collect-submodules",
        "azure.cognitiveservices.speech",
        "--add-data",
        "resources:resources",
        "--name",
        "VocalScript",
    ]
)
