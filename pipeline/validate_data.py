import pandas as pd

VALID_SALES_CHANNELS = ["Internet", "Mobile"]
VALID_TRIP_TYPES = ["RoundTrip", "OneWay", "CircleTrip"]
VALID_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def check_negative_values(df: pd.DataFrame) -> list:
    
    problems = []
    numeric_cols_that_must_be_positive = [
        "purchase_lead", "length_of_stay", "flight_duration",
        "num_passengers", "flight_hour"
    ]
    for col in numeric_cols_that_must_be_positive:
        negative_count = (df[col] < 0).sum()
        if negative_count > 0:
            problems.append(f"{col}: {negative_count} negative values found")
    return problems


def check_valid_categories(df: pd.DataFrame) -> list:
    
    problems = []

    unexpected_channels = set(df["sales_channel"].unique()) - set(VALID_SALES_CHANNELS)
    if unexpected_channels:
        problems.append(f"sales_channel: unexpected values {unexpected_channels}")

    unexpected_trip_types = set(df["trip_type"].unique()) - set(VALID_TRIP_TYPES)
    if unexpected_trip_types:
        problems.append(f"trip_type: unexpected values {unexpected_trip_types}")

    unexpected_days = set(df["flight_day"].unique()) - set(VALID_DAYS)
    if unexpected_days:
        problems.append(f"flight_day: unexpected values {unexpected_days}")

    return problems


def check_duplicates(df: pd.DataFrame) -> list:
    
    problems = []
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        problems.append(f"{duplicate_count} fully duplicate rows found")
    return problems


def check_binary_columns(df: pd.DataFrame) -> list:
    
    problems = []
    binary_cols = [
        "wants_extra_baggage", "wants_preferred_seat",
        "wants_in_flight_meals", "booking_complete"
    ]
    for col in binary_cols:
        invalid_values = set(df[col].unique()) - {0, 1}
        if invalid_values:
            problems.append(f"{col}: invalid values {invalid_values} (expected only 0/1)")
    return problems


def run_all_validations(df: pd.DataFrame) -> dict:
    
    results = {
        "negative_values": check_negative_values(df),
        "invalid_categories": check_valid_categories(df),
        "duplicates": check_duplicates(df),
        "invalid_binary_columns": check_binary_columns(df),
    }
    return results


def print_validation_report(results: dict) -> None:
    """Prints a human-readable pass/fail report."""
    print("=" * 60)
    print("DATA VALIDATION REPORT")
    print("=" * 60)

    total_problems = sum(len(v) for v in results.values())

    for check_name, problems in results.items():
        status = "PASSED" if not problems else "FAILED"
        print(f"\n[{status}] {check_name}")
        for problem in problems:
            print(f"  - {problem}")

    print("\n" + "=" * 60)
    if total_problems == 0:
        print("ALL CHECKS PASSED -- data is safe to proceed to cleaning stage.")
    else:
        print(f"{total_problems} issue(s) found -- review before proceeding.")
    print("=" * 60)


if __name__ == "__main__":
    from load_data import load_raw_data, RAW_DATA_PATH

    df = load_raw_data(RAW_DATA_PATH)
    results = run_all_validations(df)
    print_validation_report(results)