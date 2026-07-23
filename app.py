#!/usr/bin/env python3
"""
Dramatic Meeting Timer: a macOS menu bar app that plays
Helldivers drop pod music as a countdown to your next meeting.
"""

import os
from datetime import datetime, timedelta

import AVFoundation
import EventKit
import rumps
from Foundation import NSURL, NSDate

from countdown import (
    DEFAULT_LEAD_TIME_SECONDS,
    AwaitingCalendarAccess,
    CalendarEvent,
    CalendarUnavailable,
    Disabled,
    Idle,
    TimerState,
    Upcoming,
    decide_tick,
    disable,
    enable,
    normalize_lead_time,
    resolve_calendar_access,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

POLL_INTERVAL = 30
TICK_INTERVAL = 1
CALENDAR_LOOKAHEAD = timedelta(days=7)


def find_music_file() -> str | None:
    """Find the first supported audio file in the assets directory."""
    if not os.path.isdir(ASSETS_DIR):
        return None
    for f in sorted(os.listdir(ASSETS_DIR)):
        if f.lower().endswith((".mp3", ".m4a", ".wav", ".aiff")):
            return os.path.join(ASSETS_DIR, f)
    return None


class DramaticMeetingTimer(rumps.App):
    def __init__(self):
        super().__init__("", quit_button=None)
        self.state: TimerState = AwaitingCalendarAccess()
        self._pending_calendar_access_result = None
        self.music_played_for_event: tuple[str, float] | None = None

        self.music_path = find_music_file()
        self.audio_player, self.audio_error = self._load_audio_player(self.music_path)
        self.lead_time = normalize_lead_time(
            self.audio_player.duration() if self.audio_player else DEFAULT_LEAD_TIME_SECONDS
        )

        self.enable_item = rumps.MenuItem("Disable", callback=self.toggle_enabled)
        self.next_meeting_item = rumps.MenuItem("Next: —")
        self.next_meeting_item.set_callback(None)
        self.quit_item = rumps.MenuItem("Quit", callback=self.quit_app)

        self.menu = [self.next_meeting_item, self.enable_item, None, self.quit_item]

        self.event_store = EventKit.EKEventStore.alloc().init()
        self._request_calendar_access()

        self.poll_timer = rumps.Timer(self._poll_calendar, POLL_INTERVAL)
        self.poll_timer.start()
        self.tick_timer = rumps.Timer(self._tick, TICK_INTERVAL)
        self.tick_timer.start()

        self._tick(None)

    def _request_calendar_access(self):
        def handler(granted, error):
            self._pending_calendar_access_result = (bool(granted), error)

        if hasattr(self.event_store, "requestFullAccessToEventsWithCompletion_"):
            self.event_store.requestFullAccessToEventsWithCompletion_(handler)
        else:
            self.event_store.requestAccessToEntityType_completion_(
                EventKit.EKEntityTypeEvent, handler
            )

    def _poll_calendar(self, _sender):
        if not isinstance(self.state, (Idle, Upcoming)):
            return

        now = datetime.now().astimezone()
        end = now + CALENDAR_LOOKAHEAD

        try:
            predicate = self.event_store.predicateForEventsWithStartDate_endDate_calendars_(
                self._datetime_to_nsdate(now),
                self._datetime_to_nsdate(end),
                None,
            )
            events = self.event_store.eventsMatchingPredicate_(predicate) or []
        except Exception as error:
            self.state = CalendarUnavailable(f"Could not read Calendar: {error}")
            self._stop_music()
            return

        upcoming: list[CalendarEvent] = []
        for ev in events:
            if ev.isAllDay() or ev.status() == EventKit.EKEventStatusCanceled:
                continue
            start = self._nsdate_to_datetime(ev.startDate())
            if start > now:
                identifier = (
                    ev.eventIdentifier()
                    or ev.calendarItemIdentifier()
                    or f"{ev.title()}@{start.timestamp()}"
                )
                upcoming.append(CalendarEvent(identifier, ev.title(), start))

        upcoming.sort(key=lambda event: event.starts_at)
        previous_event = self.state.event if isinstance(self.state, Upcoming) else None
        next_event = upcoming[0] if upcoming else None

        if previous_event and (not next_event or previous_event.key != next_event.key):
            self._stop_music()
        self.state = Upcoming(next_event) if next_event else Idle()

    def _tick(self, _sender):
        self._consume_calendar_access_result()
        decision = decide_tick(self.state, datetime.now().astimezone(), self.lead_time)
        self.title = decision.menu_bar_title
        self.next_meeting_item.title = decision.meeting_menu_title

        if decision.refresh_calendar:
            self._poll_calendar(None)
        if decision.playback:
            self._maybe_play_music(
                decision.playback.event_key,
                decision.playback.offset_seconds,
            )

    def _consume_calendar_access_result(self):
        result = self._pending_calendar_access_result
        if result is None:
            return
        self._pending_calendar_access_result = None

        granted, error = result
        if error:
            reason = f"Calendar access failed: {error.localizedDescription()}"
        else:
            reason = "Calendar access denied"
        self.state = resolve_calendar_access(self.state, granted=granted, reason=reason)

        if granted and isinstance(self.state, Idle):
            self._poll_calendar(None)
        elif not granted:
            rumps.notification(
                "Dramatic Meeting Timer",
                reason,
                "Grant access in System Settings > Privacy & Security > Calendars",
            )

    def _maybe_play_music(self, event_key: tuple[str, float], offset_seconds: float):
        if self.music_played_for_event == event_key:
            return
        self.music_played_for_event = event_key

        if not self.audio_player:
            detail = self.audio_error or f"Place an audio file in {ASSETS_DIR}"
            rumps.notification(
                "Dramatic Meeting Timer",
                "Music unavailable",
                detail,
            )
            return

        self.audio_player.setCurrentTime_(
            min(offset_seconds, max(0.0, self.audio_player.duration() - 0.01))
        )
        self.audio_player.play()

    def toggle_enabled(self, sender):
        if isinstance(self.state, Disabled):
            self.state = enable(self.state)
            sender.title = "Disable"
            if isinstance(self.state, Idle):
                self._poll_calendar(None)
        else:
            self.state = disable(self.state)
            sender.title = "Enable"
            self._stop_music()
        self._tick(None)

    def _stop_music(self):
        if self.audio_player and self.audio_player.isPlaying():
            self.audio_player.stop()
        self.music_played_for_event = None

    def quit_app(self, _sender):
        self._stop_music()
        rumps.quit_application()

    @staticmethod
    def _datetime_to_nsdate(dt):
        return NSDate.dateWithTimeIntervalSince1970_(dt.timestamp())

    @staticmethod
    def _nsdate_to_datetime(nsdate):
        return datetime.fromtimestamp(nsdate.timeIntervalSince1970()).astimezone()

    @staticmethod
    def _load_audio_player(path):
        if not path or not os.path.exists(path):
            return None, f"Place an audio file in {ASSETS_DIR}"

        player, error = AVFoundation.AVAudioPlayer.alloc().initWithContentsOfURL_error_(
            NSURL.fileURLWithPath_(path),
            None,
        )
        if not player:
            detail = error.localizedDescription() if error else f"Could not load {path}"
            return None, detail
        player.prepareToPlay()
        return player, None


def main():
    DramaticMeetingTimer().run()


if __name__ == "__main__":
    main()
