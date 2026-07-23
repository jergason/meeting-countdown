from datetime import UTC, datetime, timedelta

from countdown import (
    AwaitingCalendarAccess,
    CalendarEvent,
    CalendarUnavailable,
    Disabled,
    Idle,
    Upcoming,
    decide_tick,
    disable,
    enable,
    resolve_calendar_access,
)

NOW = datetime(2026, 3, 23, 14, 0, tzinfo=UTC)


def event_in(seconds: float) -> CalendarEvent:
    return CalendarEvent(
        identifier="event-123",
        title="Extremely Important Goose Council",
        starts_at=NOW + timedelta(seconds=seconds),
    )


class TestTransitions:
    def test_disabling_an_upcoming_event_resumes_with_fresh_calendar_state(self):
        state = disable(Upcoming(event_in(300)))

        assert state == Disabled(Idle())
        assert enable(state) == Idle()

    def test_calendar_access_result_is_retained_while_disabled(self):
        state = resolve_calendar_access(
            Disabled(AwaitingCalendarAccess()),
            granted=True,
        )

        assert state == Disabled(Idle())

    def test_calendar_access_error_has_an_explicit_state(self):
        state = resolve_calendar_access(
            AwaitingCalendarAccess(),
            granted=False,
            reason="The calendar said no.",
        )

        assert state == CalendarUnavailable("The calendar said no.")


class TestTickDecision:
    def test_disabled_state_stays_visibly_off(self):
        decision = decide_tick(Disabled(Idle()), NOW, lead_time=40)

        assert decision.menu_bar_title == "🎵 off"
        assert decision.meeting_menu_title == "Next: —"

    def test_awaiting_access_is_distinct_from_idle(self):
        decision = decide_tick(AwaitingCalendarAccess(), NOW, lead_time=40)

        assert decision.menu_bar_title == "🎵 …"
        assert decision.meeting_menu_title == "Calendar: requesting access…"

    def test_late_countdown_seeks_to_the_correct_audio_offset(self):
        decision = decide_tick(Upcoming(event_in(10)), NOW, lead_time=40)

        assert decision.playback is not None
        assert decision.playback.offset_seconds == 30

    def test_countdown_does_not_request_early_playback(self):
        decision = decide_tick(Upcoming(event_in(41)), NOW, lead_time=40)

        assert decision.playback is None

    def test_started_event_requests_a_calendar_refresh(self):
        decision = decide_tick(Upcoming(event_in(0)), NOW, lead_time=40)

        assert decision.menu_bar_title == "🎵 NOW"
        assert decision.refresh_calendar is True
