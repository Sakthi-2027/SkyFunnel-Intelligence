import pandas as pd

RAW_DATA_PATH = "data/raw/customer_booking.csv"
PROCESSED_DATA_PATH = "data/processed/customer_booking_clean.csv"


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
 
    before_count = len(df)
    df_cleaned = df.drop_duplicates(keep="first")
    after_count = len(df_cleaned)
    removed_count = before_count - after_count

    print(f"Removed {removed_count} duplicate rows "
          f"({before_count} -> {after_count} rows)")

    return df_cleaned


def clean_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    
    df = remove_duplicates(df)
    df = df.reset_index(drop=True)
    return df


def save_cleaned_data(df: pd.DataFrame, path: str) -> None:
   
    df.to_csv(path, index=False)
    print(f"Cleaned data saved to: {path}")


if __name__ == "__main__":
    from load_data import load_raw_data

    print("Loading raw data...")
    df = load_raw_data(RAW_DATA_PATH)
    print(f"Loaded {len(df)} rows")

    print("\nCleaning data...")
    df_clean = clean_pipeline(df)

    print("\nSaving cleaned data...")
    save_cleaned_data(df_clean, PROCESSED_DATA_PATH)

    print(f"\nFinal cleaned dataset: {df_clean.shape[0]} rows, {df_clean.shape[1]} columns")