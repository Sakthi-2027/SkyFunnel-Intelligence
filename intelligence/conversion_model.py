import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from database.models import get_engine

TABLE_NAME = "bookings"

CATEGORICAL_COLUMNS = ["sales_channel", "trip_type", "flight_day", "booking_origin"]

NUMERIC_COLUMNS = [
    "num_passengers", "purchase_lead", "length_of_stay", "flight_hour",
    "wants_extra_baggage", "wants_preferred_seat", "wants_in_flight_meals",
    "flight_duration", "is_last_minute_booking", "is_weekend_flight",
    "total_extras_selected", "route_popularity", "is_long_haul"
]

TARGET_COLUMN = "booking_complete"


def load_data(engine):
    query = f"SELECT * FROM {TABLE_NAME}"
    return pd.read_sql(query, con=engine)


def prepare_features(df):
    df_encoded = pd.get_dummies(df, columns=CATEGORICAL_COLUMNS, drop_first=True)
    feature_columns = NUMERIC_COLUMNS + [
        col for col in df_encoded.columns
        if any(col.startswith(cat + "_") for cat in CATEGORICAL_COLUMNS)
    ]
    return df_encoded, feature_columns


def train_model(df_encoded, feature_columns):
    X = df_encoded[feature_columns]
    y = df_encoded[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300, max_depth=10, class_weight="balanced",
        random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    print("Accuracy:", accuracy_score(y_test, predictions))
    print("ROC AUC:", roc_auc_score(y_test, probabilities))
    print("\nClassification report:")
    print(classification_report(y_test, predictions))

    return model, feature_columns


def show_feature_importance(model, feature_columns, top_n=15):
    importances = pd.Series(model.feature_importances_, index=feature_columns)
    importances = importances.sort_values(ascending=False)
    print(f"\nTOP {top_n} FEATURE IMPORTANCES:")
    print(importances.head(top_n).to_string())


if __name__ == "__main__":
    engine = get_engine()
    df = load_data(engine)
    df_encoded, feature_columns = prepare_features(df)
    model, feature_columns = train_model(df_encoded, feature_columns)
    show_feature_importance(model, feature_columns)