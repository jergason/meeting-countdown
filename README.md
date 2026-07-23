# Dramatic Meeting Timer

A macOS menu bar app that plays [Helldivers 2 drop pod music](https://www.youtube.com/watch?v=DSesmlxKeGA) as a countdown to your next calendar event.

The song ends right as the meeting starts. You're welcome.

## Setup

Requires macOS, [uv](https://docs.astral.sh/uv/), and Homebrew's framework build of
Python 3.11. The framework build lets py2app create a standalone macOS application.

```bash
# install the build tools if needed
brew install uv python@3.11

# install dependencies
uv sync

# add your audio file
mkdir -p assets
# drop any mp3/m4a/wav/aiff file in here; the app auto-detects
# the file's duration and starts playback that many seconds before
# your meeting, so the song ends right as the meeting begins.
cp /path/to/your/song.mp3 assets/

# run it
uv run python app.py
```

The app appears in the menu bar as `🎵`. On first launch, macOS will ask for
Calendar access. Grant it. Use **Quit** in the app menu to stop it.

### Assets

The app looks for the first audio file (mp3, m4a, wav, aiff) in the `assets/`
directory. It reads the file's duration at startup and uses that as the countdown
lead time. If the app discovers a meeting after the countdown has started, it seeks
into the song so playback still finishes when the meeting begins.

## How it works

The app reads your next non-all-day, non-cancelled event during the next seven days
from **macOS Calendar** via EventKit. Any calendar synced to your Mac (Google,
Outlook/Exchange, iCloud, CalDAV) is automatically visible. No OAuth required.

### Menu bar states

| State                 | Display |
| --------------------- | ------- |
| > 1 hour              | `1.5h`  |
| < 1 hour              | `30m`   |
| < 5 min               | `4:30`  |
| < audio duration      | `T-35s` |
| Meeting started       | `NOW`   |
| Disabled              | `off`   |
| Calendar unavailable  | `!`     |

The dropdown menu shows the next meeting name and time, plus an Enable/Disable toggle.

## Build a clickable macOS app

The build uses [py2app](https://py2app.readthedocs.io/) to create a standalone,
menu-bar-only application. From the repository root:

```bash
# Install the framework Python required by py2app and the uv package manager.
brew install python@3.11 uv

# Install the exact locked dependencies.
uv sync --locked

# Add the audio that should be bundled with the app.
mkdir -p assets
cp /path/to/your/song.mp3 assets/

# Create a clean application bundle.
uv run --locked python scripts/build_app.py
```

The standalone application is created at:

```text
dist/Dramatic Meeting Timer.app
```

Double-click it in Finder or launch it from the terminal:

```bash
open "dist/Dramatic Meeting Timer.app"
```

On first launch, grant the packaged app Calendar access when macOS asks. This is
separate from permission previously granted to Terminal or Python.

The build script:

- removes stale `build/` and `dist/` output;
- includes the Python runtime and required frameworks;
- copies the audio currently in `assets/` into the bundle;
- adds the Calendar privacy descriptions to `Info.plist`; and
- verifies the completed app's code signature.

Rebuild after changing the source code, audio, or packaging configuration. To keep
the app, drag it into your `Applications` folder. It runs only in the menu bar, so
it does not add a Dock icon.

The local build is ad-hoc signed and is intended for use on the Mac that built it.
Distributing it to other people would also require a Developer ID signature and
Apple notarization.

## Development

```bash
uv run ruff check .     # lint
uv run ruff format .    # format
uv run pytest -v        # test
```

## Configuration

- **Countdown lead time** is determined automatically from your audio file's duration.
- `POLL_INTERVAL` in `app.py`: how often to check the calendar (default: 30s).
- `CALENDAR_LOOKAHEAD` in `app.py`: how far ahead to search (default: 7 days).

## Auto-start on login

Build the application and launch it manually once so macOS can ask for Calendar
access. Then open **System Settings → General → Login Items & Extensions** and add
`Dramatic Meeting Timer.app` under **Open at Login**.

## Troubleshooting

- **`!` in the menu bar:** grant Calendar access in **System Settings → Privacy &
  Security → Calendars**, then restart the app.
- **No music:** confirm exactly one supported audio file is present in `assets/`,
  then restart the app. The file is loaded at startup.
- **Build asks for a framework Python:** rebuild the generated environment with
  Homebrew Python, then sync again:

  ```bash
  uv venv --clear --python "$(brew --prefix python@3.11)/bin/python3.11"
  uv sync --locked
  ```
