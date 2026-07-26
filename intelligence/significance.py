from scipy import stats
import pandas as pd
from database.models import get_engine

TABLE_NAME = "bookings"

SIGNIFICANCE_THRESHOLD = 0.05


def binomial_significance_test(observed_successes, observed_total, baseline_rate):
    result = stats.binomtest(observed_successes, observed_total, baseline_rate, alternative="two-sided")
    return result.pvalue


def is_significant_anomaly(observed_successes, observed_total, baseline_rate):
    p_value = binomial_significance_test(observed_successes, observed_total, baseline_rate)
    return p_value < SIGNIFICANCE_THRESHOLD, p_value


def check_routes_against_origin_baseline(engine, routes):
    route_list = "', '".join(routes)
    query = f"""
        SELECT route, booking_origin, booking_complete
        FROM {TABLE_NAME}
        WHERE route IN ('{route_list}')
    """
    raw_df = pd.read_sql(query, con=engine)

    dominant_origin = raw_df.groupby("route")["booking_origin"].agg(lambda x: x.mode()[0])

    route_stats = raw_df.groupby("route")["booking_complete"].agg(total="count", completed="sum")
    route_stats["booking_origin"] = dominant_origin

    origins = route_stats["booking_origin"].unique().tolist()
    origin_list = "', '".join(origins)
    baseline_query = f"""
        SELECT booking_origin, AVG(booking_complete) as baseline_rate
        FROM {TABLE_NAME}
        WHERE booking_origin IN ('{origin_list}')
        GROUP BY booking_origin
    """
    baseline_df = pd.read_sql(baseline_query, con=engine)

    merged = route_stats.reset_index().merge(baseline_df, on="booking_origin")

    results = []
    for _, row in merged.iterrows():
        significant, p_value = is_significant_anomaly(
            int(row["completed"]), int(row["total"]), row["baseline_rate"]
        )
        results.append({
            "route": row["route"],
            "booking_origin": row["booking_origin"],
            "total": row["total"],
            "completed": row["completed"],
            "baseline_rate": row["baseline_rate"],
            "p_value": p_value,
            "is_significant_anomaly": significant
        })

    return pd.DataFrame(results).sort_values("p_value")

if __name__ == "__main__":
    engine = get_engine()

    zero_conversion_routes = [
        "REPTPE", "MELPUS", "IKASYD", "IKAPER", "IKAOOL",
        "IKAMEL", "ICNKBV", "DELSYD", "DELSIN", "AKLICN"
    ]

    results_df = check_routes_against_origin_baseline(engine, zero_conversion_routes)
    print(results_df.to_string(index=False))