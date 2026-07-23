import os
from types import SimpleNamespace

import EventKit

import app
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


def test_assets_dir_uses_bundle_resources_when_frozen(monkeypatch):
    monkeypatch.setattr(app.sys, "frozen", "macosx_app", raising=False)
    monkeypatch.setenv("RESOURCEPATH", "/Example.app/Contents/Resources")

    assert app.assets_dir() == os.path.join(
        "/Example.app/Contents/Resources",
        "assets",
    )


def test_assets_dir_uses_source_tree_during_development(monkeypatch):
    monkeypatch.delattr(app.sys, "frozen", raising=False)
    monkeypatch.delenv("RESOURCEPATH", raising=False)

    assert app.assets_dir() == os.path.join(app.SCRIPT_DIR, "assets")
