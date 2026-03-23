"""Pure display logic for countdown formatting — no macOS dependencies."""

from datetime import datetime

LEAD_TIME_SECONDS = 40


def format_countdown(remaining_seconds: float) -> str:
    """Format remaining seconds into a menu bar title string."""
    if remaining_seconds <= LEAD_TIME_SECONDS:
        secs = int(remaining_seconds)
        return f"🔊 T-{secs}s"
    elif remaining_seconds <= 300:
        mins = int(remaining_seconds // 60)
        secs = int(remaining_seconds % 60)
        return f"🎵 {mins}:{secs:02d}"
    elif remaining_seconds <= 3600:
        mins = int(remaining_seconds // 60)
        return f"🎵 {mins}m"
    else:
        hrs = remaining_seconds / 3600
        return f"🎵 {hrs:.1f}h"


def format_menu_item(event_title: str | None, event_start: datetime) -> str:
    """Format the dropdown menu item showing next meeting info."""
    name = event_title or "—"
    if len(name) > 30:
        name = name[:27] + "..."
    time_str = event_start.strftime("%-I:%M %p")
    return f"Next: {name} @ {time_str}"
