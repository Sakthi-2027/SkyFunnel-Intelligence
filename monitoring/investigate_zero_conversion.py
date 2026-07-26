import pandas as pd
from database.models import get_engine

TABLE_NAME = "bookings"

ZERO_CONVERSION_ROUTES = [
    "REPTPE", "MELPUS", "IKASYD", "IKAPER", "IKAOOL",
    "IKAMEL", "ICNKBV", "DELSYD", "DELSIN", "AKLICN"
]


def get_route_data(engine, routes):
    route_list = "', '".join(routes)
    query = f"""
        SELECT *
        FROM {TABLE_NAME}
        WHERE route IN ('{route_list}')
    """
    return pd.read_sql(query, con=engine)


def compare_booking_origin(df):
    return df.groupby("route")["booking_origin"].agg(lambda x: x.mode()[0])


def compare_sales_channel_mix(df):
    return df.groupby("route")["sales_channel"].value_counts(normalize=True).unstack()


def compare_averages(df):
    return df.groupby("route").agg(
        avg_purchase_lead=("purchase_lead", "mean"),
        avg_length_of_stay=("length_of_stay", "mean"),
        avg_flight_duration=("flight_duration", "mean"),
        total_bookings=("booking_complete", "count")
    )


def check_other_routes_same_origin(engine, df):
    origins = df["booking_origin"].unique().tolist()
    origin_list = "', '".join(origins)
    query = f"""
        SELECT booking_origin, AVG(booking_complete) as conversion_rate, COUNT(*) as total
        FROM {TABLE_NAME}
        WHERE booking_origin IN ('{origin_list}')
        GROUP BY booking_origin
        ORDER BY conversion_rate DESC
    """
    return pd.read_sql(query, con=engine)


if __name__ == "__main__":
    engine = get_engine()
    df = get_route_data(engine, ZERO_CONVERSION_ROUTES)

    print("=" * 60)
    print("INVESTIGATING ZERO-CONVERSION ROUTES")
    print("=" * 60)

    print("\nBOOKING ORIGIN PER ROUTE:")
    print(compare_booking_origin(df))

    print("\nSALES CHANNEL MIX PER ROUTE:")
    print(compare_sales_channel_mix(df))

    print("\nAVERAGES PER ROUTE:")
    print(compare_averages(df).to_string())

    print("\nCONVERSION RATE OF THESE ORIGIN COUNTRIES OVERALL (across ALL their routes):")
    print(check_other_routes_same_origin(engine, df).to_string(index=False))