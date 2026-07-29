from datetime import datetime
from database.models import get_engine
from monitoring.conversion_metrics import (
    overall_conversion_rate, conversion_by_channel,
    conversion_by_trip_type, conversion_by_route
)
from intelligence.health_score import calculate_health_score, get_monitored_routes
from intelligence.business_impact import calculate_route_impact
from intelligence.root_cause import explain_channel_gap, explain_route

REPORTS_DIR = "reports"


def build_report(engine):
    lines = []
    lines.append("=" * 70)
    lines.append("SKYFUNNEL INTELLIGENCE -- EXECUTIVE REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    health = calculate_health_score(engine)
    lines.append(f"\nBOOKING HEALTH SCORE: {health['overall_score']} / 100 -- {health['status']}")
    lines.append(f"  Conversion Health : {health['conversion_score']} / 100")
    lines.append(f"  Anomaly Health    : {health['anomaly_score']} / 100 ({health['significant_anomalies']} routes flagged)")
    lines.append(f"  Impact Health     : {health['impact_score']} / 100")
    lines.append(f"  Channel Health    : {health['channel_score']} / 100")

    lines.append("\n" + "-" * 70)
    lines.append("OVERALL CONVERSION")
    lines.append("-" * 70)
    overall = overall_conversion_rate(engine)
    lines.append(f"Platform-wide conversion rate: {overall:.2%}")

    lines.append("\n" + "-" * 70)
    lines.append("CHANNEL PERFORMANCE")
    lines.append("-" * 70)
    lines.append(explain_channel_gap(engine))

    lines.append("\n" + "-" * 70)
    lines.append("TOP 5 ROUTES BY CONVERSION")
    lines.append("-" * 70)
    top_routes = conversion_by_route(engine).head(5)
    lines.append(top_routes.to_string(index=False))

    lines.append("\n" + "-" * 70)
    lines.append("WORST 5 ROUTES BY CONVERSION")
    lines.append("-" * 70)
    bottom_routes = conversion_by_route(engine).tail(5)
    lines.append(bottom_routes.to_string(index=False))

    lines.append("\n" + "-" * 70)
    lines.append("TOP 5 BUSINESS-IMPACT INCIDENTS (by estimated lost bookings)")
    lines.append("-" * 70)
    monitored_routes = get_monitored_routes(engine)
    impacts = [calculate_route_impact(engine, r) for r in monitored_routes]
    significant_impacts = [i for i in impacts if i["is_significant"] and i["estimated_lost_bookings"] > 0]
    significant_impacts.sort(key=lambda x: x["estimated_lost_bookings"], reverse=True)

    for incident in significant_impacts[:5]:
        lines.append(
            f"  {incident['route']} ({incident['origin']}): "
            f"~{incident['estimated_lost_bookings']} lost bookings "
            f"(p={incident['p_value']:.4f})"
        )

    lines.append("\n" + "-" * 70)
    lines.append("ROOT CAUSE DETAIL -- TOP INCIDENT")
    lines.append("-" * 70)
    if significant_impacts:
        top_incident_route = significant_impacts[0]["route"]
        lines.append(explain_route(engine, top_incident_route))

    lines.append("\n" + "-" * 70)
    lines.append("RECOMMENDED ACTIONS")
    lines.append("-" * 70)
    recommendations = generate_recommendations(health, significant_impacts)
    for rec in recommendations:
        lines.append(f"  - {rec}")

    lines.append("\n" + "=" * 70)

    return "\n".join(lines)


def generate_recommendations(health, significant_impacts):
    recs = []

    if health["status"] in ["WARNING", "CRITICAL"]:
        recs.append(f"Overall health is {health['status']} -- prioritize investigation this week.")

    if health["channel_gap"] > 0.03:
        recs.append(
            f"Mobile conversion trails Internet by {health['channel_gap']:.1%} -- "
            f"review mobile checkout flow for friction points."
        )

    if significant_impacts:
        worst = significant_impacts[0]
        recs.append(
            f"Route {worst['route']} shows the highest estimated impact "
            f"(~{worst['estimated_lost_bookings']} lost bookings) -- investigate first."
        )

    recs.append(
        f"{len(significant_impacts)} routes show statistically significant deviation from baseline -- "
        f"note that at this sample size, some are expected to be false positives; "
        f"prioritize by impact size, not p-value alone."
    )

    return recs


def save_report(report_text):
    filename = f"{REPORTS_DIR}/executive_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, "w") as f:
        f.write(report_text)
    return filename


if __name__ == "__main__":
    engine = get_engine()
    report = build_report(engine)
    print(report)

    saved_path = save_report(report)
    print(f"\nReport saved to: {saved_path}")