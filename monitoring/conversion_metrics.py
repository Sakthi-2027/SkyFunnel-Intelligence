import pandas as pd
from database.models import get_engine

TABLE_NAME = "bookings"


def overall_conversion_rate(engine) -> float:
    query = f"SELECT AVG(booking_complete) as rate FROM {TABLE_NAME}"
    result = pd.read_sql(query, con=engine)
    return result["rate"][0]

def conversion_by_channel(engine) -> pd.DataFrame:
    query = f"""
        SELECT
            sales_channel,
            COUNT(*) as total_bookings,
            AVG(booking_complete) as conversion_rate
        FROM {TABLE_NAME}
        GROUP BY sales_channel
        ORDER BY conversion_rate DESC
    """
    return pd.read_sql(query, con=engine)


def conversion_by_route(engine, min_bookings: int = 50) -> pd.DataFrame:
    query = f"""
        SELECT
            route,
            COUNT(*) as total_bookings,
            AVG(booking_complete) as conversion_rate
        FROM {TABLE_NAME}
        GROUP BY route
        HAVING COUNT(*) >= {min_bookings}
        ORDER BY conversion_rate DESC
    """
    return pd.read_sql(query, con=engine)


def conversion_by_trip_type(engine) -> pd.DataFrame:
    query = f"""
        SELECT
            trip_type,
            COUNT(*) as total_bookings,
            AVG(booking_complete) as conversion_rate
        FROM {TABLE_NAME}
        GROUP BY trip_type
        ORDER BY conversion_rate DESC
    """
    return pd.read_sql(query, con=engine)


def conversion_last_minute_vs_planned(engine) -> pd.DataFrame:
    query = f"""
        SELECT
            is_last_minute_booking,
            COUNT(*) as total_bookings,
            AVG(booking_complete) as conversion_rate
        FROM {TABLE_NAME}
        GROUP BY is_last_minute_booking
    """
    return pd.read_sql(query, con=engine)


def print_monitoring_report(engine) -> None:
    print("=" * 60)
    print("SKYFUNNEL INTELLIGENCE -- CONVERSION MONITORING REPORT")
    print("=" * 60)

    overall = overall_conversion_rate(engine)
    print(f"\nOVERALL CONVERSION RATE: {overall:.2%}")

    print("\n--- BY SALES CHANNEL ---")
    print(conversion_by_channel(engine).to_string(index=False))

    print("\n--- BY TRIP TYPE ---")
    print(conversion_by_trip_type(engine).to_string(index=False))

    print("\n--- LAST-MINUTE VS PLANNED ---")
    print(conversion_last_minute_vs_planned(engine).to_string(index=False))

    print("\n--- TOP 10 ROUTES BY CONVERSION (min 50 bookings) ---")
    routes = conversion_by_route(engine).head(10)
    print(routes.to_string(index=False))

    print("\n--- BOTTOM 10 ROUTES BY CONVERSION (min 50 bookings) ---")
    routes_bottom = conversion_by_route(engine).tail(10)
    print(routes_bottom.to_string(index=False))

    print("\n" + "=" * 60)


if __name__ == "__main__":
    engine = get_engine()
    print_monitoring_report(engine)