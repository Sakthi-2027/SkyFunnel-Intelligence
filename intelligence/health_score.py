import pandas as pd
from database.models import get_engine
from monitoring.conversion_metrics import overall_conversion_rate, conversion_by_channel
from intelligence.business_impact import calculate_route_impact

TABLE_NAME = "bookings"
KNOWN_BASELINE_CONVERSION = 0.15


def get_monitored_routes(engine, min_bookings=50):
    query = f"""
        SELECT route FROM {TABLE_NAME}
        GROUP BY route
        HAVING COUNT(*) >= {min_bookings}
    """
    return pd.read_sql(query, con=engine)["route"].tolist()


def score_conversion_health(engine):
    current_rate = overall_conversion_rate(engine)
    ratio = current_rate / KNOWN_BASELINE_CONVERSION
    score = min(100, max(0, ratio * 100))
    return score, current_rate


def score_anomaly_health(engine, routes):
    results = [calculate_route_impact(engine, route) for route in routes]
    significant_count = sum(1 for r in results if r["is_significant"])
    total_routes = len(routes)
    healthy_ratio = 1 - (significant_count / total_routes)
    score = healthy_ratio * 100
    return score, significant_count, total_routes


def score_impact_health(engine, routes, max_tolerable_loss=200):
    results = [calculate_route_impact(engine, route) for route in routes]
    total_lost = sum(r["estimated_lost_bookings"] for r in results)
    ratio = total_lost / max_tolerable_loss
    score = min(100, max(0, (1 - ratio) * 100))
    return score, total_lost


def score_channel_health(engine):
    channel_df = conversion_by_channel(engine)
    internet_rate = channel_df[channel_df["sales_channel"] == "Internet"]["conversion_rate"].iloc[0]
    mobile_rate = channel_df[channel_df["sales_channel"] == "Mobile"]["conversion_rate"].iloc[0]
    gap = internet_rate - mobile_rate
    max_tolerable_gap = 0.10
    ratio = gap / max_tolerable_gap
    score = min(100, max(0, (1 - ratio) * 100))
    return score, gap


def classify_health(score):
    if score >= 85:
        return "HEALTHY"
    elif score >= 70:
        return "MONITOR"
    elif score >= 50:
        return "WARNING"
    else:
        return "CRITICAL"


def calculate_health_score(engine):
    monitored_routes = get_monitored_routes(engine)

    conversion_score, current_rate = score_conversion_health(engine)
    anomaly_score, significant_count, total_routes = score_anomaly_health(engine, monitored_routes)
    impact_score, total_lost = score_impact_health(engine, monitored_routes)
    channel_score, channel_gap = score_channel_health(engine)

    weighted_score = (
        conversion_score * 0.40 +
        anomaly_score * 0.25 +
        impact_score * 0.20 +
        channel_score * 0.15
    )

    status = classify_health(weighted_score)

    return {
        "overall_score": round(weighted_score, 1),
        "status": status,
        "conversion_score": round(conversion_score, 1),
        "current_conversion_rate": current_rate,
        "anomaly_score": round(anomaly_score, 1),
        "significant_anomalies": f"{significant_count}/{total_routes}",
        "impact_score": round(impact_score, 1),
        "estimated_lost_bookings": round(total_lost, 1),
        "channel_score": round(channel_score, 1),
        "channel_gap": channel_gap
    }


def print_health_report(result):
    print("=" * 60)
    print("SKYFUNNEL INTELLIGENCE -- BOOKING HEALTH SCORE")
    print("=" * 60)
    print(f"\nOVERALL SCORE: {result['overall_score']} / 100 -- {result['status']}")
    print("\nBreakdown:")
    print(f"  Conversion Health   : {result['conversion_score']} / 100 (current rate: {result['current_conversion_rate']:.2%})")
    print(f"  Anomaly Health      : {result['anomaly_score']} / 100 ({result['significant_anomalies']} monitored routes flagged)")
    print(f"  Impact Health       : {result['impact_score']} / 100 (~{result['estimated_lost_bookings']} estimated lost bookings)")
    print(f"  Channel Health      : {result['channel_score']} / 100 (Mobile-Internet gap: {result['channel_gap']:.1%})")
    print("=" * 60)


if __name__ == "__main__":
    engine = get_engine()
    result = calculate_health_score(engine)
    print_health_report(result)