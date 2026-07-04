from sklearn.ensemble import IsolationForest


def detect_anomalies(data, feature_columns, contamination):
    """
    Detect unusual machine readings using Isolation Forest.

    Returns a copy of the original data containing:
    - anomaly_status
    - anomaly_score
    """

    result = data.copy()

    feature_data = result[feature_columns]

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42
    )

    predictions = model.fit_predict(feature_data)

    result["anomaly_status"] = [
        "Anomaly" if prediction == -1 else "Normal"
        for prediction in predictions
    ]

    # Isolation Forest's normal decision score becomes lower
    # for unusual observations. Negating it makes larger values
    # easier to interpret as more unusual.
    result["anomaly_score"] = -model.decision_function(
        feature_data
    )

    return result