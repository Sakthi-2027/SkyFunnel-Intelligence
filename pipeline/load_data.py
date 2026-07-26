
import pandas as pd  

RAW_DATA_PATH = "data/raw/customer_booking.csv"

def load_raw_data(path: str) -> pd.DataFrame:
    
    df = pd.read_csv(path, encoding="latin-1")
    return df


def inspect_data(df: pd.DataFrame) -> None:
    
    print("=" * 60)
    print("SHAPE (rows, columns):", df.shape)
    print("=" * 60)

    print("\nCOLUMN NAMES AND DATA TYPES:")
    print(df.dtypes)

    print("\nFIRST 5 ROWS:")
    print(df.head())

    print("\nMISSING VALUES PER COLUMN:")
    print(df.isnull().sum())

    print("\nBOOKING COMPLETION RATE (our target column):")

    completion_rate = df["booking_complete"].mean()
    print(f"{completion_rate:.2%} of bookings were completed")



if __name__ == "__main__":
    data = load_raw_data(RAW_DATA_PATH)
    inspect_data(data)