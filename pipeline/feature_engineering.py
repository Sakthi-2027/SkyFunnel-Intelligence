import pandas as pd

CLEANED_DATA_PATH = "data/processed/customer_booking_clean.csv"
FEATURED_DATA_PATH = "data/processed/customer_booking_featured.csv"
LAST_MINUTE_THRESHOLD_DAYS = 7

WEEKEND_DAYS = ["Sat", "Sun"]


def add_last_minute_flag(df: pd.DataFrame) -> pd.DataFrame:
    
    df["is_last_minute_booking"] = (
        df["purchase_lead"] <= LAST_MINUTE_THRESHOLD_DAYS
    ).astype(int)
    return df


def add_weekend_flight_flag(df: pd.DataFrame) -> pd.DataFrame:
    
    df["is_weekend_flight"] = df["flight_day"].isin(WEEKEND_DAYS).astype(int)
    return df


def add_total_extras(df: pd.DataFrame) -> pd.DataFrame:
    
    df["total_extras_selected"] = (
        df["wants_extra_baggage"]
        + df["wants_preferred_seat"]
        + df["wants_in_flight_meals"]
    )
    return df


def add_route_popularity(df: pd.DataFrame) -> pd.DataFrame:
    
    route_counts = df["route"].value_counts()
    df["route_popularity"] = df["route"].map(route_counts)
    return df


def add_long_haul_flag(df: pd.DataFrame) -> pd.DataFrame:
    
    df["is_long_haul"] = (df["flight_duration"] >= 8).astype(int)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Runs every feature engineering step in order."""
    df = add_last_minute_flag(df)
    df = add_weekend_flight_flag(df)
    df = add_total_extras(df)
    df = add_route_popularity(df)
    df = add_long_haul_flag(df)
    return df


def save_featured_data(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
    print(f"Featured data saved to: {path}")


if __name__ == "__main__":
    print("Loading cleaned data...")
    df = pd.read_csv(CLEANED_DATA_PATH)
    print(f"Loaded {len(df)} rows")

    print("\nEngineering features...")
    df = engineer_features(df)
    new_columns = [
        "is_last_minute_booking", "is_weekend_flight",
        "total_extras_selected", "route_popularity", "is_long_haul"
    ]
    print(f"Added {len(new_columns)} new columns: {new_columns}")

    print("\nSaving featured data...")
    save_featured_data(df, FEATURED_DATA_PATH)

    print(f"\nFinal dataset shape: {df.shape}")
    print("\nPreview of new columns:")
    print(df[new_columns].head())