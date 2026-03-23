from datetime import datetime

from countdown import format_countdown, format_menu_item


class TestFormatCountdown:
    def test_in_lead_time_zone(self):
        assert format_countdown(35) == "🔊 T-35s"

    def test_at_exact_lead_time(self):
        assert format_countdown(40) == "🔊 T-40s"

    def test_one_second_left(self):
        assert format_countdown(1) == "🔊 T-1s"

    def test_fractional_seconds_truncated(self):
        assert format_countdown(10.7) == "🔊 T-10s"

    def test_within_five_minutes(self):
        assert format_countdown(150) == "🎵 2:30"

    def test_just_over_lead_time(self):
        assert format_countdown(41) == "🎵 0:41"

    def test_five_minutes_exactly(self):
        assert format_countdown(300) == "🎵 5:00"

    def test_within_one_hour(self):
        assert format_countdown(1800) == "🎵 30m"

    def test_just_over_five_minutes(self):
        assert format_countdown(301) == "🎵 5m"

    def test_over_one_hour(self):
        assert format_countdown(5400) == "🎵 1.5h"

    def test_several_hours(self):
        assert format_countdown(10800) == "🎵 3.0h"


class TestFormatMenuItem:
    def test_basic(self):
        dt = datetime(2026, 3, 23, 14, 30)
        assert format_menu_item("Standup", dt) == "Next: Standup @ 2:30 PM"

    def test_none_title(self):
        dt = datetime(2026, 3, 23, 9, 0)
        assert format_menu_item(None, dt) == "Next: — @ 9:00 AM"

    def test_long_title_truncated(self):
        dt = datetime(2026, 3, 23, 16, 15)
        long_name = "Q4 Cross-Functional Alignment Sync Retro"
        result = format_menu_item(long_name, dt)
        assert len(result.split(" @ ")[0]) <= len("Next: ") + 30
        assert "..." in result

    def test_exactly_30_chars_not_truncated(self):
        dt = datetime(2026, 3, 23, 10, 0)
        name = "a" * 30
        result = format_menu_item(name, dt)
        assert "..." not in result
