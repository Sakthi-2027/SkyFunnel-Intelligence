import pandas as pd
from pipeline.feature_engineering import (
    add_last_minute_flag, add_weekend_flight_flag,
    add_total_extras, add_long_haul_flag
)


def test_last_minute_flag_correctly_identifies_threshold():
    df = pd.DataFrame({"purchase_lead": [3, 7, 8, 100]})
    result = add_last_minute_flag(df)
    assert list(result["is_last_minute_booking"]) == [1, 1, 0, 0]


def test_weekend_flight_flag_identifies_sat_sun():
    df = pd.DataFrame({"flight_day": ["Mon", "Sat", "Sun", "Wed"]})
    result = add_weekend_flight_flag(df)
    assert list(result["is_weekend_flight"]) == [0, 1, 1, 0]


def test_total_extras_sums_correctly():
    df = pd.DataFrame({
        "wants_extra_baggage": [1, 0, 1],
        "wants_preferred_seat": [1, 1, 0],
        "wants_in_flight_meals": [0, 0, 1]
    })
    result = add_total_extras(df)
    assert list(result["total_extras_selected"]) == [2, 1, 2]


def test_long_haul_flag_uses_eight_hour_threshold():
    df = pd.DataFrame({"flight_duration": [4.5, 7.9, 8.0, 12.0]})
    result = add_long_haul_flag(df)
    assert list(result["is_long_haul"]) == [0, 0, 1, 1]