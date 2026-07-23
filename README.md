# Dramatic Meeting Timer

A macOS menu bar app that plays [Helldivers 2 drop pod music](https://www.youtube.com/watch?v=DSesmlxKeGA) as a countdown to your next calendar event.

The song ends right as the meeting starts. You're welcome.

## Setup

Requires macOS and [uv](https://docs.astral.sh/uv/). The repository pins Python
3.11 through `.python-version`; uv will use or install it during setup.

```bash
# install uv if needed
brew install uv

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

Run the app manually once first so macOS can ask for Calendar access. Then create a
LaunchAgent using absolute paths:

```bash
# Replace /absolute/path/to/dramatic-meeting-timer below with this repository's path.
mkdir -p ~/Library/LaunchAgents
$EDITOR ~/Library/LaunchAgents/com.dramatic-meeting-timer.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dramatic-meeting-timer</string>
    <key>ProgramArguments</key>
    <array>
        <string>/absolute/path/to/dramatic-meeting-timer/.venv/bin/python</string>
        <string>/absolute/path/to/dramatic-meeting-timer/app.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/absolute/path/to/dramatic-meeting-timer</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Load it:

```bash
launchctl bootout gui/"$(id -u)" ~/Library/LaunchAgents/com.dramatic-meeting-timer.plist 2>/dev/null || true
launchctl bootstrap gui/"$(id -u)" ~/Library/LaunchAgents/com.dramatic-meeting-timer.plist
```

## Troubleshooting

- **`!` in the menu bar:** grant Calendar access in **System Settings → Privacy &
  Security → Calendars**, then restart the app.
- **No music:** confirm exactly one supported audio file is present in `assets/`,
  then restart the app. The file is loaded at startup.
- **LaunchAgent does not start:** confirm both absolute paths in the plist exist and
  run `plutil -lint ~/Library/LaunchAgents/com.dramatic-meeting-timer.plist`.
