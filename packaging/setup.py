"""Build a standalone macOS application with py2app."""

from pathlib import Path

from setuptools import setup

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
SUPPORTED_AUDIO_SUFFIXES = {".mp3", ".m4a", ".wav", ".aiff"}
AUDIO_FILES = (
    sorted(
        path
        for path in ASSETS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_SUFFIXES
    )
    if ASSETS_DIR.is_dir()
    else []
)

if not AUDIO_FILES:
    raise SystemExit("Add an audio file to assets/ before building the app.")

CALENDAR_USAGE_DESCRIPTION = (
    "Dramatic Meeting Timer reads upcoming events to time its musical countdown."
)

setup(
    name="Dramatic Meeting Timer",
    version="0.1.0",
    app=[
        {
            "script": str(ROOT / "app.py"),
            "dest_base": "Dramatic Meeting Timer",
        }
    ],
    data_files=[("assets", [str(path) for path in AUDIO_FILES])],
    options={
        "py2app": {
            "argv_emulation": False,
            "bdist_base": str(ROOT / "build"),
            "dist_dir": str(ROOT / "dist"),
            "includes": ["AVFoundation", "EventKit", "Foundation"],
            "packages": ["rumps"],
            "plist": {
                "CFBundleDisplayName": "Dramatic Meeting Timer",
                "CFBundleIdentifier": "dance.jamison.dramatic-meeting-timer",
                "CFBundleName": "Dramatic Meeting Timer",
                "CFBundleShortVersionString": "0.1.0",
                "CFBundleVersion": "1",
                "LSUIElement": True,
                "NSCalendarsFullAccessUsageDescription": CALENDAR_USAGE_DESCRIPTION,
                "NSCalendarsUsageDescription": CALENDAR_USAGE_DESCRIPTION,
                "NSHighResolutionCapable": True,
                "NSRequiresAquaSystemAppearance": False,
            },
        }
    },
)
