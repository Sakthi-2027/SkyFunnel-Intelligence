import pandas as pd
from sklearn.ensemble import IsolationForest
from database.models import get_engine

TABLE_NAME = "bookings"

FEATURE_COLUMNS = [
    "num_passengers", "length_of_stay", "flight_hour",
    "wants_extra_baggage", "wants_preferred_seat", "wants_in_flight_meals",
    "flight_duration", "is_weekend_flight", "total_extras_selected", "is_long_haul"
]

CONTAMINATION = 0.02


def load_data(engine):
    query = f"SELECT * FROM {TABLE_NAME}"
    return pd.read_sql(query, con=engine)


def run_isolation_forest(df):
    model = IsolationForest(contamination=CONTAMINATION, random_state=42, n_estimators=200)
    predictions = model.fit_predict(df[FEATURE_COLUMNS])
    scores = model.decision_function(df[FEATURE_COLUMNS])
    df["anomaly_flag"] = predictions
    df["anomaly_score"] = scores
    return df, model


def summarize_anomalies(df):
    anomalies = df[df["anomaly_flag"] == -1].sort_values("anomaly_score")
    print(f"Total rows: {len(df)}")
    print(f"Flagged anomalies: {len(anomalies)} ({len(anomalies)/len(df):.2%})")
    print(f"\nAnomaly conversion rate: {anomalies['booking_complete'].mean():.2%}")
    print(f"Normal conversion rate: {df[df['anomaly_flag'] == 1]['booking_complete'].mean():.2%}")

    print("\nAnomaly rate by sales_channel:")
    print(df.groupby("sales_channel")["anomaly_flag"].apply(lambda x: (x == -1).mean()))

    print("\nAnomaly rate by trip_type:")
    print(df.groupby("trip_type")["anomaly_flag"].apply(lambda x: (x == -1).mean()))

    return anomalies


def show_worst_anomalies(anomalies, n=10):
    cols_to_show = ["route", "booking_origin", "sales_channel", "purchase_lead",
                     "flight_duration", "total_extras_selected", "booking_complete", "anomaly_score"]
    print(f"\nTOP {n} MOST ANOMALOUS BOOKINGS:")
    print(anomalies[cols_to_show].head(n).to_string(index=False))


if __name__ == "__main__":
    engine = get_engine()
    df = load_data(engine)
    df, model = run_isolation_forest(df)
    anomalies = summarize_anomalies(df)
    show_worst_anomalies(anomalies)
