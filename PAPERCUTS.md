# Papercuts

Small frictions whose plausible fixes would change version-controlled files in this repository. Logged via `papercuts`.

2026-07-23T15:25:06.477Z - gpt-5.6-sol - Jamison Dance

pyproject.toml declares the dramatic-meeting-timer console script, but the project has no build-system/package configuration, so uv treats it as virtual and does not create .venv/bin/dramatic-meeting-timer. Either package the app properly or remove the inert entry point.

2026-07-23T15:36:12.178Z - gpt-5.6-sol - Jamison Dance

The project did not pin a Python interpreter, so uv reused a Homebrew Python 3.14 environment that cannot report the macOS version and refuses to sync. Track a .python-version so setup converges on the tested Python 3.11 runtime.

2026-07-23T16:00:33.430Z - gpt-5.6-sol - Jamison Dance

The project pinned Python 3.11 but allowed uv to choose its portable non-framework build, which py2app cannot use to create a standalone macOS bundle. Prefer a system framework Python for this macOS app and make the build script validate that prerequisite.

2026-07-23T16:01:43.919Z - gpt-5.6-sol - Jamison Dance

The py2app build inherits PEP 621 runtime dependencies from pyproject.toml as install_requires, but py2app rejects install_requires and aborts before creating the bundle. The packaging command needs isolated metadata or an explicit empty install_requires value so dependencies are discovered from the synced environment instead.
