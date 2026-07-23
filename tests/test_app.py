from types import SimpleNamespace

import EventKit

from app import DramaticMeetingTimer


class ModernEventStore:
    def requestFullAccessToEventsWithCompletion_(self, handler):  # noqa: N802
        handler(True, None)


class LegacyEventStore:
    def __init__(self):
        self.entity_type = None

    def requestAccessToEntityType_completion_(self, entity_type, handler):  # noqa: N802
        self.entity_type = entity_type
        handler(True, None)


def test_requests_modern_calendar_access_without_blocking():
    timer = SimpleNamespace(
        event_store=ModernEventStore(),
        _pending_calendar_access_result=None,
    )

    DramaticMeetingTimer._request_calendar_access(timer)

    assert timer._pending_calendar_access_result == (True, None)


def test_falls_back_to_legacy_calendar_access_api():
    store = LegacyEventStore()
    timer = SimpleNamespace(
        event_store=store,
        _pending_calendar_access_result=None,
    )

    DramaticMeetingTimer._request_calendar_access(timer)

    assert store.entity_type == EventKit.EKEntityTypeEvent
    assert timer._pending_calendar_access_result == (True, None)
