import pandas as pd
from database.models import get_engine
from monitoring.conversion_metrics import overall_conversion_rate, conversion_by_channel, conversion_by_route
from intelligence.significance import is_significant_anomaly

TABLE_NAME = "bookings"


def explain_route(engine, route, min_bookings=50):
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

    overall_rate = overall_conversion_rate(engine)

    significant, p_value = is_significant_anomaly(completed, total, baseline_rate)

    lines = []
    lines.append(f"ROUTE {route}: {observed_rate:.1%} conversion ({completed}/{total} bookings)")
    lines.append(f"  Platform-wide baseline: {overall_rate:.1%}")
    lines.append(f"  Dominant origin country: {origin} (typical rate: {baseline_rate:.1%})")

    if significant:
        direction = "below" if observed_rate < baseline_rate else "above"
        lines.append(f"  VERDICT: Statistically significant anomaly (p={p_value:.4f}) -- "
                      f"{route} converts meaningfully {direction} what {origin} normally does. "
                      f"This points to a route-specific issue, not general {origin} customer behavior.")
    else:
        lines.append(f"  VERDICT: Not statistically significant (p={p_value:.4f}) -- "
                      f"{route}'s low conversion is consistent with {origin}'s normal baseline. "
                      f"Likely reflects regional customer behavior, not a route-specific problem.")

    return "\n".join(lines)


def explain_channel_gap(engine):
    channel_df = conversion_by_channel(engine)
    overall_rate = overall_conversion_rate(engine)

    internet_row = channel_df[channel_df["sales_channel"] == "Internet"].iloc[0]
    mobile_row = channel_df[channel_df["sales_channel"] == "Mobile"].iloc[0]

    gap = internet_row["conversion_rate"] - mobile_row["conversion_rate"]

    significant, p_value = is_significant_anomaly(
        int(mobile_row["conversion_rate"] * mobile_row["total_bookings"]),
        int(mobile_row["total_bookings"]),
        internet_row["conversion_rate"]
    )

    lines = []
    lines.append(f"CHANNEL GAP: Mobile converts at {mobile_row['conversion_rate']:.1%} "
                  f"vs Internet at {internet_row['conversion_rate']:.1%} "
                  f"(a {gap:.1%} point gap, on {int(mobile_row['total_bookings'])} mobile bookings)")

    if significant:
        lines.append(f"  VERDICT: Statistically significant (p={p_value:.4f}) -- "
                      f"this is unlikely to be random variance. Worth investigating the "
                      f"mobile checkout flow specifically.")
    else:
        lines.append(f"  VERDICT: Not statistically significant (p={p_value:.4f}).")

    return "\n".join(lines)


if __name__ == "__main__":
    engine = get_engine()

    print("=" * 60)
    print("SKYFUNNEL INTELLIGENCE -- ROOT CAUSE REPORT")
    print("=" * 60)

    print("\n" + explain_channel_gap(engine))

    print("\n" + "-" * 60)
    routes_to_check = ["DELSYD", "AKLICN", "IKAOOL", "PENTPE"]
    for route in routes_to_check:
        print("\n" + explain_route(engine, route))