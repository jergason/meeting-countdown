# Papercuts

Small frictions whose plausible fixes would change version-controlled files in this repository. Logged via `papercuts`.

2026-07-23T15:25:06.477Z - gpt-5.6-sol - Jamison Dance

pyproject.toml declares the dramatic-meeting-timer console script, but the project has no build-system/package configuration, so uv treats it as virtual and does not create .venv/bin/dramatic-meeting-timer. Either package the app properly or remove the inert entry point.

2026-07-23T15:36:12.178Z - gpt-5.6-sol - Jamison Dance

The project did not pin a Python interpreter, so uv reused a Homebrew Python 3.14 environment that cannot report the macOS version and refuses to sync. Track a .python-version so setup converges on the tested Python 3.11 runtime.
