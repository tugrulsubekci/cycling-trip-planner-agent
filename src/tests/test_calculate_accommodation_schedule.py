"""Tests for calculate_accommodation_schedule tool."""


from src.tools.calculate_accommodation_schedule import (
    calculate_accommodation_schedule,
    parse_pattern,
)


class TestCalculateAccommodationSchedule:
    """Tests for calculate_accommodation_schedule tool."""

    def test_calculate_accommodation_schedule_success(self):
        """Test successful schedule calculation."""
        result = calculate_accommodation_schedule.func(
            total_nights=10, preference_pattern="every 4th night", accommodation_type="hostel"
        )

        assert isinstance(result, dict)
        assert result["total_nights"] == 10
        assert result["schedule"][4] == "hostel"
        assert result["schedule"][8] == "hostel"
        assert 4 in result["special_nights"]
        assert 8 in result["special_nights"]
        assert result["schedule"][1] == "camping"  # default
        assert result["schedule"][2] == "camping"  # default

    def test_calculate_accommodation_schedule_custom_default(self):
        """Test schedule with custom default type."""
        result = calculate_accommodation_schedule.func(
            total_nights=6,
            preference_pattern="every 3 nights",
            accommodation_type="hotel",
            default_type="hostel",
        )

        assert result["schedule"][3] == "hotel"
        assert result["schedule"][6] == "hotel"
        assert result["schedule"][1] == "hostel"  # custom default
        assert result["schedule"][2] == "hostel"  # custom default

    def test_calculate_accommodation_schedule_every_3_nights(self):
        """Test pattern 'every 3 nights'."""
        result = calculate_accommodation_schedule.func(
            total_nights=9, preference_pattern="every 3 nights", accommodation_type="hostel"
        )

        assert 3 in result["special_nights"]
        assert 6 in result["special_nights"]
        assert 9 in result["special_nights"]
        assert len(result["special_nights"]) == 3

    def test_calculate_accommodation_schedule_invalid_pattern(self):
        """Test invalid pattern format."""
        result = calculate_accommodation_schedule.func(
            total_nights=10, preference_pattern="invalid pattern", accommodation_type="hostel"
        )

        assert "error" in result
        assert "Could not parse pattern" in result["error"]

    def test_calculate_accommodation_schedule_invalid_period(self):
        """Test invalid period (non-positive)."""
        # This should be caught by pattern parsing, but test the logic
        result = calculate_accommodation_schedule.func(
            total_nights=10, preference_pattern="every 0th night", accommodation_type="hostel"
        )

        # Pattern parsing should fail, but if it somehow parsed, period validation should catch it
        assert "error" in result

    def test_calculate_accommodation_schedule_invalid_total_nights(self):
        """Test invalid total_nights (non-positive)."""
        result = calculate_accommodation_schedule.func(
            total_nights=0, preference_pattern="every 4th night", accommodation_type="hostel"
        )

        assert "error" in result
        assert "Total nights must be positive" in result["error"]

    def test_calculate_accommodation_schedule_no_special_nights(self):
        """Test when pattern results in no special nights."""
        # 10 nights, every 15th night -> no special nights
        result = calculate_accommodation_schedule.func(
            total_nights=10, preference_pattern="every 15th night", accommodation_type="hostel"
        )

        assert len(result["special_nights"]) == 0
        assert all(acc_type == "camping" for acc_type in result["schedule"].values())


class TestParsePattern:
    """Tests for parse_pattern helper function."""

    def test_parse_pattern_every_4th_night(self):
        """Test parsing 'every 4th night'."""
        assert parse_pattern("every 4th night") == 4

    def test_parse_pattern_every_3_nights(self):
        """Test parsing 'every 3 nights'."""
        assert parse_pattern("every 3 nights") == 3

    def test_parse_pattern_case_insensitive(self):
        """Test pattern parsing is case-insensitive."""
        assert parse_pattern("EVERY 5TH NIGHT") == 5
        assert parse_pattern("Every 6Th NiGhT") == 6

    def test_parse_pattern_ordinals(self):
        """Test parsing with different ordinals."""
        assert parse_pattern("every 1st night") == 1
        assert parse_pattern("every 2nd night") == 2
        assert parse_pattern("every 3rd night") == 3

    def test_parse_pattern_invalid(self):
        """Test parsing invalid patterns."""
        assert parse_pattern("invalid pattern") is None
        assert parse_pattern("every night") is None
        assert parse_pattern("") is None
