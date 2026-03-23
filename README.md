# Dramatic Meeting Timer

A macOS menu bar app that plays [Helldivers 2 drop pod music](https://www.youtube.com/watch?v=DSesmlxKeGA) as a ~40 second countdown to your next calendar event.

The song ends right as the meeting starts. You're welcome.

## Setup

Requires Python 3.11+, [uv](https://docs.astral.sh/uv/).

```bash
# install dependencies
uv sync

# add your audio file
mkdir -p assets
# drop any mp3/m4a/wav/aiff file in here — the app auto-detects
# the file's duration and starts playback that many seconds before
# your meeting, so the song ends right as the meeting begins.
cp /path/to/your/song.mp3 assets/

# run it
uv run python app.py
```

On first launch, macOS will ask for calendar access — grant it.

### Assets

The app looks for the first audio file (mp3, m4a, wav, aiff) in the `assets/` directory. It reads the file's duration at startup and uses that as the countdown lead time — so whatever song you pick, it'll finish right as your meeting starts.

## How it works

The app reads your next meeting from **macOS Calendar** via EventKit. Any calendar synced to your Mac (Google, Outlook/Exchange, iCloud, CalDAV) is automatically visible — no OAuth required.

### Menu bar states

| State                 | Display |
| --------------------- | ------- |
| > 1 hour              | `1.5h`  |
| < 1 hour              | `30m`   |
| < 5 min               | `4:30`  |
| < 40s (music playing) | `T-35s` |
| Meeting started       | `NOW`   |
| Disabled              | `off`   |

The dropdown menu shows the next meeting name and time, plus an Enable/Disable toggle.

## Development

```bash
uv run ruff check .     # lint
uv run ruff format .    # format
uv run pytest -v        # test
```

## Configuration

- **Countdown lead time** is determined automatically from your audio file's duration. No config needed.
- `POLL_INTERVAL` in `app.py` — how often to check the calendar (default: 30s)

## Auto-start on login

```bash
# create a launchd plist (adjust the path to your clone)
cat > ~/Library/LaunchAgents/com.dramatic-meeting-timer.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dramatic-meeting-timer</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd /path/to/meeting-countdown && uv run python app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF
```
