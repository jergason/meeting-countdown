#!/usr/bin/env python3
"""Build a clean, standalone Dramatic Meeting Timer.app."""

import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_PATH = ROOT / "dist" / "Dramatic Meeting Timer.app"


def main() -> None:
    if not sysconfig.get_config_var("PYTHONFRAMEWORK"):
        raise SystemExit(
            "Packaging requires a macOS framework build of Python 3.11.\n"
            "Run `brew install python@3.11`, remove `.venv`, and run `uv sync`."
        )

    for directory in (ROOT / "build", ROOT / "dist"):
        shutil.rmtree(directory, ignore_errors=True)

    print("Building Dramatic Meeting Timer.app…")
    result = subprocess.run(
        [sys.executable, "setup.py", "py2app"],
        cwd=ROOT / "packaging",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode:
        print(result.stdout, file=sys.stderr)
        raise SystemExit(result.returncode)

    if not APP_PATH.is_dir():
        raise SystemExit(f"Build finished without creating {APP_PATH}")

    bundled_audio = APP_PATH / "Contents" / "Resources" / "assets"
    if not any(bundled_audio.iterdir()):
        raise SystemExit(f"Build did not include an audio file in {bundled_audio}")

    subprocess.run(
        ["codesign", "--verify", "--deep", "--strict", str(APP_PATH)],
        check=True,
    )

    print(f"\nBuilt {APP_PATH}")
    print(f"Open it with: open {APP_PATH!s}")


if __name__ == "__main__":
    main()
