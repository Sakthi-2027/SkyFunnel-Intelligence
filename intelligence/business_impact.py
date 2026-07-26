import pandas as pd
from database.models import get_engine
from intelligence.significance import is_significant_anomaly

TABLE_NAME = "bookings"


def calculate_route_impact(engine, route):
    query = f"""
        SELECT booking_origin, COUNT(*) as total, SUM(booking_complete) as completed
        FROM {TABLE_NAME}
        WHERE route = '{route}'
        GROUP BY booking_origin
        ORDER BY total DESC
        LIMIT 1
    """
    row = pd.read_sql(query, con=engine).iloc[0]
    origin = row["booking_origin"]
    total = int(row["total"])
    completed = int(row["completed"])
    observed_rate = completed / total

    baseline_query = f"""
        SELECT AVG(booking_complete) as baseline_rate
        FROM {TABLE_NAME}
        WHERE booking_origin = '{origin}'
    """
    baseline_rate = pd.read_sql(baseline_query, con=engine)["baseline_rate"][0]

    expected_completions = total * baseline_rate
    lost_bookings = expected_completions - completed

    significant, p_value = is_significant_anomaly(completed, total, baseline_rate)

    severity = classify_severity(lost_bookings, total)

    return {
        "route": route,
        "origin": origin,
        "total_bookings": total,
        "actual_completions": completed,
        "expected_completions": round(expected_completions, 1),
        "estimated_lost_bookings": round(lost_bookings, 1),
        "observed_rate": observed_rate,
        "baseline_rate": baseline_rate,
        "is_significant": significant,
        "p_value": p_value,
        "severity": severity
    }


def classify_severity(lost_bookings, total_bookings):
    lost_pct = lost_bookings / total_bookings if total_bookings > 0 else 0

    if lost_bookings <= 0:
        return "NONE"
    elif lost_pct < 0.05:
        return "LOW"
    elif lost_pct < 0.10:
        return "MEDIUM"
    else:
        return "HIGH"


def print_impact_report(engine, routes):
    print("=" * 70)
    print("SKYFUNNEL INTELLIGENCE -- BUSINESS IMPACT REPORT")
    print("=" * 70)

    results = [calculate_route_impact(engine, route) for route in routes]
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("estimated_lost_bookings", ascending=False)

    for _, row in results_df.iterrows():
        print(f"\nROUTE {row['route']} ({row['origin']}) -- Severity: {row['severity']}")
        print(f"  Actual completions: {row['actual_completions']} / {row['total_bookings']} bookings ({row['observed_rate']:.1%})")
        print(f"  Expected at baseline ({row['baseline_rate']:.1%}): {row['expected_completions']} completions")
        print(f"  Estimated lost bookings: {row['estimated_lost_bookings']}")
        print(f"  Statistically significant: {row['is_significant']} (p={row['p_value']:.4f})")

    total_lost = results_df["estimated_lost_bookings"].sum()
    print("\n" + "=" * 70)
    print(f"TOTAL ESTIMATED LOST BOOKINGS ACROSS THESE ROUTES: {total_lost:.1f}")
    print("=" * 70)


if __name__ == "__main__":
    engine = get_engine()
    routes_to_check = ["DELSYD", "AKLICN", "ICNKBV", "DELSIN", "MELPUS", "IKASYD", "REPTPE"]
    print_impact_report(engine, routes_to_check)