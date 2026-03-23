#!/usr/bin/env python3
"""
Dramatic Meeting Timer — a macOS menu bar app that plays
Helldivers drop pod music as a countdown to your next meeting.
"""

import os
import subprocess
import threading
from datetime import datetime, timedelta

import EventKit
import rumps

from countdown import LEAD_TIME_SECONDS, format_countdown, format_menu_item

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_PATH = os.path.join(SCRIPT_DIR, "assets", "drop_pod.mp3")

POLL_INTERVAL = 30
TICK_INTERVAL = 1


class DramaticMeetingTimer(rumps.App):
    def __init__(self):
        super().__init__("", quit_button=None)
        self.enabled = True
        self.next_event_title = None
        self.next_event_start = None
        self.music_process = None
        self.music_played_for_event = None

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

        self._poll_calendar(None)

    def _request_calendar_access(self):
        semaphore = threading.Semaphore(0)
        granted_ref = [False]

        def handler(granted, error):
            granted_ref[0] = granted
            semaphore.release()

        self.event_store.requestFullAccessToEventsWithCompletion_(handler)
        semaphore.acquire(timeout=10)

        if not granted_ref[0]:
            rumps.notification(
                "Dramatic Meeting Timer",
                "Calendar access denied",
                "Grant calendar access in System Settings > Privacy & Security > Calendars",
            )

    def _poll_calendar(self, _sender):
        if not self.enabled:
            return

        now = datetime.now()
        end = now + timedelta(hours=4)

        ns_now = self._datetime_to_nsdate(now)
        ns_end = self._datetime_to_nsdate(end)

        predicate = self.event_store.predicateForEventsWithStartDate_endDate_calendars_(
            ns_now, ns_end, None
        )
        events = self.event_store.eventsMatchingPredicate_(predicate)

        if not events:
            self.next_event_title = None
            self.next_event_start = None
            return

        upcoming = []
        for ev in events:
            if ev.isAllDay():
                continue
            start = self._nsdate_to_datetime(ev.startDate())
            if start > now:
                upcoming.append((start, ev.title()))

        upcoming.sort(key=lambda x: x[0])

        if upcoming:
            self.next_event_start, self.next_event_title = upcoming[0]
        else:
            self.next_event_title = None
            self.next_event_start = None

    def _tick(self, _sender):
        if not self.enabled or not self.next_event_start:
            self.title = "🎵 —"
            self.next_meeting_item.title = "Next: —"
            return

        now = datetime.now()
        remaining = (self.next_event_start - now).total_seconds()

        if remaining <= 0:
            self.title = "🎵 NOW"
            self._poll_calendar(None)
            return

        result = format_countdown(remaining)
        self.title = result
        self.next_meeting_item.title = format_menu_item(
            self.next_event_title, self.next_event_start
        )

        if remaining <= LEAD_TIME_SECONDS:
            self._maybe_play_music()

    def _maybe_play_music(self):
        event_key = (self.next_event_title, self.next_event_start)
        if self.music_played_for_event == event_key:
            return
        self.music_played_for_event = event_key

        if not os.path.exists(MUSIC_PATH):
            rumps.notification(
                "Dramatic Meeting Timer",
                "Music file missing",
                f"Expected: {MUSIC_PATH}",
            )
            return

        self.music_process = subprocess.Popen(
            ["afplay", MUSIC_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def toggle_enabled(self, sender):
        self.enabled = not self.enabled
        sender.title = "Disable" if self.enabled else "Enable"
        if not self.enabled:
            self.title = "🎵 off"
            self._stop_music()

    def _stop_music(self):
        if self.music_process and self.music_process.poll() is None:
            self.music_process.terminate()
            self.music_process = None

    def quit_app(self, _sender):
        self._stop_music()
        rumps.quit_application()

    @staticmethod
    def _datetime_to_nsdate(dt):
        from Foundation import NSDate

        return NSDate.dateWithTimeIntervalSince1970_(dt.timestamp())

    @staticmethod
    def _nsdate_to_datetime(nsdate):
        return datetime.fromtimestamp(nsdate.timeIntervalSince1970())


def main():
    DramaticMeetingTimer().run()


if __name__ == "__main__":
    main()
