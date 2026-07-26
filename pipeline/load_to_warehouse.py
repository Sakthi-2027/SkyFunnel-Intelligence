import pandas as pd
from database.models import get_engine, create_tables

FEATURED_DATA_PATH = "data/processed/customer_booking_featured.csv"
TABLE_NAME = "bookings"


def load_to_database(df: pd.DataFrame, engine) -> None:
    df.to_sql(TABLE_NAME, con=engine, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into '{TABLE_NAME}' table")


def verify_load(engine) -> None:
    result = pd.read_sql(f"SELECT COUNT(*) as row_count FROM {TABLE_NAME}", con=engine)
    print(f"Verification: database now contains {result['row_count'][0]} rows")


if __name__ == "__main__":
    print("Setting up database engine...")
    engine = get_engine()
    create_tables(engine)

    print("\nLoading featured data...")
    df = pd.read_csv(FEATURED_DATA_PATH)

    print("\nWriting to warehouse...")
    load_to_database(df, engine)

    print("\nVerifying...")
    verify_load(engine)