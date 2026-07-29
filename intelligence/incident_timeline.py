from datetime import datetime
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database.models import get_engine, create_tables, Incident
from intelligence.health_score import get_monitored_routes
from intelligence.business_impact import calculate_route_impact

TABLE_NAME = "incidents"


def detect_and_log_incidents(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    monitored_routes = get_monitored_routes(engine)
    impacts = [calculate_route_impact(engine, r) for r in monitored_routes]
    real_incidents = [
        i for i in impacts
        if i["is_significant"] and i["estimated_lost_bookings"] > 0
    ]

    logged_count = 0
    for incident in real_incidents:
        existing = session.query(Incident).filter_by(route=incident["route"]).first()
        if existing:
            continue

        new_incident = Incident(
            detected_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            route=incident["route"],
            origin=incident["origin"],
            issue_type="Low conversion vs origin baseline",
            observed_rate=incident["observed_rate"],
            baseline_rate=incident["baseline_rate"],
            p_value=incident["p_value"],
            estimated_lost_bookings=incident["estimated_lost_bookings"],
            severity=incident["severity"],
            status="New",
            notes=""
        )
        session.add(new_incident)
        logged_count += 1

    session.commit()
    session.close()
    return logged_count


def print_timeline(engine):
    query = f"SELECT * FROM {TABLE_NAME} ORDER BY estimated_lost_bookings DESC"
    df = pd.read_sql(query, con=engine)
    print(f"Total logged incidents: {len(df)}")
    print(df[["route", "origin", "estimated_lost_bookings", "severity", "status", "detected_at"]].to_string(index=False))


if __name__ == "__main__":
    engine = get_engine()
    create_tables(engine)

    logged_count = detect_and_log_incidents(engine)
    print(f"Logged {logged_count} new incidents")

    print("\nCURRENT INCIDENT TIMELINE:")
    print_timeline(engine)