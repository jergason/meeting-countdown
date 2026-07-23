"""Pure state and display logic with no macOS dependencies."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

DEFAULT_LEAD_TIME_SECONDS = 40


@dataclass(frozen=True)
class CalendarEvent:
    identifier: str
    title: str | None
    starts_at: datetime

    @property
    def key(self) -> tuple[str, float]:
        return (self.identifier, self.starts_at.timestamp())


@dataclass(frozen=True)
class AwaitingCalendarAccess:
    pass


@dataclass(frozen=True)
class CalendarUnavailable:
    reason: str


@dataclass(frozen=True)
class Idle:
    pass


@dataclass(frozen=True)
class Upcoming:
    event: CalendarEvent


ResumeState = AwaitingCalendarAccess | CalendarUnavailable | Idle


@dataclass(frozen=True)
class Disabled:
    resume_state: ResumeState


TimerState = Disabled | AwaitingCalendarAccess | CalendarUnavailable | Idle | Upcoming


@dataclass(frozen=True)
class PlaybackRequest:
    event_key: tuple[str, float]
    offset_seconds: float


@dataclass(frozen=True)
class TickDecision:
    menu_bar_title: str
    meeting_menu_title: str
    refresh_calendar: bool = False
    playback: PlaybackRequest | None = None


def format_countdown(
    remaining_seconds: float, lead_time: float = DEFAULT_LEAD_TIME_SECONDS
) -> str:
    """Format remaining seconds into a menu bar title string."""
    if remaining_seconds <= lead_time:
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


def normalize_lead_time(duration_seconds: float) -> float:
    """Return a usable countdown duration for an audio file."""
    if not isfinite(duration_seconds) or duration_seconds <= 0:
        return DEFAULT_LEAD_TIME_SECONDS
    return duration_seconds


def disable(state: TimerState) -> Disabled:
    """Disable the timer while retaining only the state needed to resume."""
    if isinstance(state, Disabled):
        return state
    if isinstance(state, Upcoming):
        return Disabled(Idle())
    return Disabled(state)


def enable(state: Disabled) -> ResumeState:
    """Restore the state retained when the timer was disabled."""
    return state.resume_state


def resolve_calendar_access(
    state: TimerState, *, granted: bool, reason: str = "Calendar access denied"
) -> TimerState:
    """Apply an asynchronous calendar-access result to the current state."""
    resolved: ResumeState = Idle() if granted else CalendarUnavailable(reason)
    if isinstance(state, Disabled):
        return Disabled(resolved)
    return resolved


def decide_tick(state: TimerState, now: datetime, lead_time: float) -> TickDecision:
    """Decide what the macOS adapter should render and which effects it should run."""
    if isinstance(state, Disabled):
        return TickDecision("🎵 off", "Next: —")
    if isinstance(state, AwaitingCalendarAccess):
        return TickDecision("🎵 …", "Calendar: requesting access…")
    if isinstance(state, CalendarUnavailable):
        return TickDecision("🎵 !", "Calendar: access unavailable")
    if isinstance(state, Idle):
        return TickDecision("🎵 —", "Next: —")

    event = state.event
    remaining = (event.starts_at - now).total_seconds()
    if remaining <= 0:
        return TickDecision("🎵 NOW", format_menu_item(event.title, event.starts_at), True)

    playback = None
    if remaining <= lead_time:
        playback = PlaybackRequest(
            event_key=event.key,
            offset_seconds=max(0.0, lead_time - remaining),
        )

    return TickDecision(
        format_countdown(remaining, lead_time),
        format_menu_item(event.title, event.starts_at),
        playback=playback,
    )
