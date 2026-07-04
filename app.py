import pandas as pd
import plotly.express as px
import streamlit as st

from ml_utils import detect_anomalies

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Machine Health Dashboard",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Machine Health Monitoring Dashboard")

st.write(
    "Upload machine sensor data, compare multiple machines, "
    "identify abnormal operating conditions, and prioritise maintenance."
)

st.caption(
    "The thresholds used in this project are for educational and "
    "demonstration purposes only. They are not certified industrial limits."
)

with st.expander("About this project and how to use it"):
    st.markdown(
        """
        This dashboard is a Python-based machine health monitoring tool built
        using Streamlit, Pandas, Plotly, and Scikit-learn.

        It helps users analyse machine sensor data by:
        - Uploading machine readings through CSV files
        - Validating data format and numerical values
        - Ranking machines by maintenance risk
        - Explaining why a machine is marked Healthy, Warning, or Critical
        - Comparing sensor readings interactively
        - Analysing historical sensor trends
        - Detecting unusual historical readings using Isolation Forest

        **How to use the dashboard:**

        1. Use the sample CSV files or upload your own machine data.
        2. Adjust risk thresholds from the sidebar if needed.
        3. Filter machines by health status.
        4. Inspect individual machines to understand their risk factors.
        5. Use the historical section to observe sensor trends over time.
        6. Use the anomaly detection section to identify unusual readings.

        **Note:** This project is built for educational and portfolio purposes.
        The results should not be treated as certified industrial maintenance advice.
        """
    )


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

st.markdown("#### Upload or try sample data")

sample_csv = """machine_id,temperature,vibration,rpm,torque,operating_hours
M001,68,2.1,1450,32,420
M002,91,5.8,1600,41,870
M003,74,3.2,1520,35,610
M004,105,7.1,1700,48,1100
M005,62,1.7,1380,29,300
M006,115,8.2,1800,52,1400
"""

st.download_button(
    label="Download Sample CSV",
    data=sample_csv,
    file_name="sample_machine_data.csv",
    mime="text/csv"
)

uploaded_file = st.file_uploader(
    "Upload machine data",
    type=["csv"]
)


try:
    if uploaded_file is not None:
        machine_data = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully.")
    else:
        machine_data = pd.read_csv("machine_data.csv")
        st.info("Displaying the default sample machine data.")

except FileNotFoundError:
    st.error("The default machine_data.csv file could not be found.")
    st.stop()

except pd.errors.EmptyDataError:
    st.error("The uploaded CSV file is empty.")
    st.stop()

except pd.errors.ParserError:
    st.error("The CSV file could not be read. Please check its format.")
    st.stop()


# --------------------------------------------------
# COLUMN VALIDATION
# --------------------------------------------------

required_columns = [
    "machine_id",
    "temperature",
    "vibration",
    "rpm",
    "torque",
    "operating_hours"
]

missing_columns = [
    column
    for column in required_columns
    if column not in machine_data.columns
]

if missing_columns:
    st.error(
        "The CSV file is missing these required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()


# --------------------------------------------------
# NUMERICAL DATA VALIDATION
# --------------------------------------------------

numeric_columns = [
    "temperature",
    "vibration",
    "rpm",
    "torque",
    "operating_hours"
]

for column in numeric_columns:
    machine_data[column] = pd.to_numeric(
        machine_data[column],
        errors="coerce"
    )

invalid_rows = machine_data[
    machine_data[numeric_columns].isnull().any(axis=1)
]

if not invalid_rows.empty:
    st.error(
        "Some rows contain missing or invalid numerical values."
    )

    st.write("Problematic rows:")

    st.dataframe(
        invalid_rows,
        use_container_width=True,
        hide_index=True
    )

    st.stop()

st.success("The machine data is valid.")


# --------------------------------------------------
# SIDEBAR THRESHOLD SETTINGS
# --------------------------------------------------

st.sidebar.header("Risk Threshold Settings")

st.sidebar.caption(
    "Adjust the warning and critical limits used by the dashboard."
)

temperature_warning = st.sidebar.number_input(
    "Temperature warning limit (°C)",
    min_value=0.0,
    value=85.0,
    step=1.0
)

temperature_critical = st.sidebar.number_input(
    "Temperature critical limit (°C)",
    min_value=0.0,
    value=100.0,
    step=1.0
)

vibration_warning = st.sidebar.number_input(
    "Vibration warning limit",
    min_value=0.0,
    value=4.0,
    step=0.1
)

vibration_critical = st.sidebar.number_input(
    "Vibration critical limit",
    min_value=0.0,
    value=6.0,
    step=0.1
)

rpm_warning = st.sidebar.number_input(
    "RPM warning limit",
    min_value=0,
    value=1550,
    step=50
)

rpm_critical = st.sidebar.number_input(
    "RPM critical limit",
    min_value=0,
    value=1650,
    step=50
)

torque_warning = st.sidebar.number_input(
    "Torque warning limit",
    min_value=0.0,
    value=38.0,
    step=1.0
)

torque_critical = st.sidebar.number_input(
    "Torque critical limit",
    min_value=0.0,
    value=45.0,
    step=1.0
)

hours_warning = st.sidebar.number_input(
    "Operating-hours warning limit",
    min_value=0,
    value=700,
    step=50
)

hours_critical = st.sidebar.number_input(
    "Operating-hours critical limit",
    min_value=0,
    value=1000,
    step=50
)


# --------------------------------------------------
# THRESHOLD VALIDATION
# --------------------------------------------------

invalid_thresholds = (
    temperature_warning >= temperature_critical
    or vibration_warning >= vibration_critical
    or rpm_warning >= rpm_critical
    or torque_warning >= torque_critical
    or hours_warning >= hours_critical
)

if invalid_thresholds:
    st.error(
        "Every warning limit must be lower than its critical limit."
    )
    st.stop()


# --------------------------------------------------
# RISK-SCORE FUNCTIONS
# --------------------------------------------------

def calculate_risk_score(row):
    score = 0

    if row["temperature"] > temperature_critical:
        score += 3
    elif row["temperature"] > temperature_warning:
        score += 1

    if row["vibration"] > vibration_critical:
        score += 3
    elif row["vibration"] > vibration_warning:
        score += 1

    if row["rpm"] > rpm_critical:
        score += 3
    elif row["rpm"] > rpm_warning:
        score += 1

    if row["torque"] > torque_critical:
        score += 3
    elif row["torque"] > torque_warning:
        score += 1

    if row["operating_hours"] > hours_critical:
        score += 3
    elif row["operating_hours"] > hours_warning:
        score += 1

    return score


def assign_health_status(score):
    if score >= 8:
        return "Critical"
    elif score >= 4:
        return "Warning"
    else:
        return "Healthy"

def assign_maintenance_action(score):
    if score >= 8:
        return "Immediate inspection required"

    elif score >= 4:
        return "Schedule maintenance soon"

    else:
        return "Continue routine monitoring"

def identify_risk_factors(row):
    reasons = []

    if row["temperature"] > temperature_critical:
        reasons.append(
            "Temperature exceeds the critical limit"
        )
    elif row["temperature"] > temperature_warning:
        reasons.append(
            "Temperature exceeds the warning limit"
        )

    if row["vibration"] > vibration_critical:
        reasons.append(
            "Vibration exceeds the critical limit"
        )
    elif row["vibration"] > vibration_warning:
        reasons.append(
            "Vibration exceeds the warning limit"
        )

    if row["rpm"] > rpm_critical:
        reasons.append(
            "RPM exceeds the critical limit"
        )
    elif row["rpm"] > rpm_warning:
        reasons.append(
            "RPM exceeds the warning limit"
        )

    if row["torque"] > torque_critical:
        reasons.append(
            "Torque exceeds the critical limit"
        )
    elif row["torque"] > torque_warning:
        reasons.append(
            "Torque exceeds the warning limit"
        )

    if row["operating_hours"] > hours_critical:
        reasons.append(
            "Operating hours exceed the critical maintenance limit"
        )
    elif row["operating_hours"] > hours_warning:
        reasons.append(
            "Operating hours exceed the warning maintenance limit"
        )

    if not reasons:
        reasons.append(
            "All readings are within the selected operating limits"
        )

    return reasons


# --------------------------------------------------
# CALCULATE MACHINE HEALTH
# --------------------------------------------------

machine_data["risk_score"] = machine_data.apply(
    calculate_risk_score,
    axis=1
)

machine_data["health_status"] = machine_data[
    "risk_score"
].apply(assign_health_status)

machine_data["maintenance_action"] = machine_data[
    "risk_score"
].apply(assign_maintenance_action)

ranked_data = machine_data.sort_values(
    by="risk_score",
    ascending=False
)


# --------------------------------------------------
# SIDEBAR FILTER
# --------------------------------------------------

st.sidebar.divider()

st.sidebar.subheader("Dashboard Filters")

selected_statuses = st.sidebar.multiselect(
    "Show machines with status",
    options=[
        "Healthy",
        "Warning",
        "Critical"
    ],
    default=[
        "Healthy",
        "Warning",
        "Critical"
    ]
)

if not selected_statuses:
    st.warning(
        "Select at least one machine-health status."
    )
    st.stop()

filtered_data = ranked_data[
    ranked_data["health_status"].isin(selected_statuses)
]

if filtered_data.empty:
    st.warning(
        "No machines match the selected health-status filters."
    )
    st.stop()


# --------------------------------------------------
# DASHBOARD SUMMARY
# --------------------------------------------------

total_machines = len(filtered_data)

healthy_count = (
    filtered_data["health_status"] == "Healthy"
).sum()

warning_count = (
    filtered_data["health_status"] == "Warning"
).sum()

critical_count = (
    filtered_data["health_status"] == "Critical"
).sum()

column1, column2, column3, column4 = st.columns(4)

column1.metric(
    label="Total Machines",
    value=total_machines
)

column2.metric(
    label="Healthy",
    value=int(healthy_count)
)

column3.metric(
    label="Warning",
    value=int(warning_count)
)

column4.metric(
    label="Critical",
    value=int(critical_count)
)


# --------------------------------------------------
# MACHINE RISK TABLE
# --------------------------------------------------

st.subheader("Machine Risk Ranking")

st.dataframe(
    filtered_data,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# DOWNLOADABLE REPORT
# --------------------------------------------------

report_csv = filtered_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Machine Report",
    data=report_csv,
    file_name="machine_health_report.csv",
    mime="text/csv"
)


# --------------------------------------------------
# RISK-SCORE CHART
# --------------------------------------------------

st.subheader("Risk Score Comparison")

risk_chart = px.bar(
    filtered_data,
    x="machine_id",
    y="risk_score",
    color="health_status",
    title="Machine Risk Scores",
    labels={
        "machine_id": "Machine",
        "risk_score": "Risk Score",
        "health_status": "Health Status"
    }
)

st.plotly_chart(
    risk_chart,
    use_container_width=True
)


# --------------------------------------------------
# SENSOR COMPARISON EXPLORER
# --------------------------------------------------

st.subheader("Sensor Comparison Explorer")

sensor_options = {
    "Temperature (°C)": "temperature",
    "Vibration": "vibration",
    "RPM": "rpm",
    "Torque": "torque",
    "Operating Hours": "operating_hours"
}

selected_sensor_label = st.selectbox(
    "Choose a sensor parameter to compare",
    options=list(sensor_options.keys()),
    key="sensor_comparison_selector"
)

selected_sensor_column = sensor_options[
    selected_sensor_label
]

sensor_data = filtered_data.sort_values(
    by=selected_sensor_column,
    ascending=False
)

sensor_average = sensor_data[
    selected_sensor_column
].mean()

highest_sensor_row = sensor_data.loc[
    sensor_data[selected_sensor_column].idxmax()
]

summary1, summary2 = st.columns(2)

summary1.metric(
    label=f"Average {selected_sensor_label}",
    value=round(sensor_average, 2)
)

summary2.metric(
    label="Highest Reading",
    value=(
        f"{highest_sensor_row['machine_id']} — "
        f"{round(highest_sensor_row[selected_sensor_column], 2)}"
    )
)

sensor_chart = px.bar(
    sensor_data,
    x="machine_id",
    y=selected_sensor_column,
    color="health_status",
    title=f"{selected_sensor_label} Comparison",
    labels={
        "machine_id": "Machine",
        selected_sensor_column: selected_sensor_label,
        "health_status": "Health Status"
    },
    hover_data={
        "risk_score": True
    }
)

st.plotly_chart(
    sensor_chart,
    use_container_width=True
)


# --------------------------------------------------
# HISTORICAL SENSOR TREND EXPLORER
# --------------------------------------------------


st.subheader("Historical Sensor Trends")

st.write(
    "Inspect how a selected machine's sensor readings change over time."
)

st.markdown("#### Upload or try sample historical data")

sample_history_csv = """timestamp,machine_id,temperature,vibration,rpm,torque,operating_hours
2026-07-01 08:00,M001,66,1.8,1440,31,415
2026-07-01 10:00,M001,67,1.9,1445,31,417
2026-07-01 12:00,M001,68,2.0,1450,32,419
2026-07-01 14:00,M001,69,2.1,1455,32,421
2026-07-01 16:00,M001,70,2.2,1460,33,423
2026-07-01 08:00,M002,84,4.3,1570,38,865
2026-07-01 10:00,M002,86,4.6,1580,39,867
2026-07-01 12:00,M002,88,5.0,1590,40,869
2026-07-01 14:00,M002,90,5.4,1600,41,871
2026-07-01 16:00,M002,92,5.8,1610,42,873
2026-07-01 08:00,M004,94,5.8,1640,43,1095
2026-07-01 10:00,M004,97,6.1,1660,44,1097
2026-07-01 12:00,M004,100,6.5,1680,46,1099
2026-07-01 14:00,M004,103,6.8,1690,47,1101
2026-07-01 16:00,M004,106,7.2,1710,49,1103
2026-07-01 08:00,M006,101,6.6,1690,47,1395
2026-07-01 10:00,M006,105,7.0,1720,49,1397
2026-07-01 12:00,M006,109,7.4,1750,50,1399
2026-07-01 14:00,M006,113,7.8,1780,51,1401
2026-07-01 16:00,M006,117,8.3,1810,53,1403
"""

st.download_button(
    label="Download Sample Historical CSV",
    data=sample_history_csv,
    file_name="sample_machine_history.csv",
    mime="text/csv"
)

uploaded_history_file = st.file_uploader(
    "Upload historical machine data",
    type=["csv"],
    key="historical_data_uploader"
)

try:
    if uploaded_history_file is not None:
        history_data = pd.read_csv(uploaded_history_file)
        st.success("Historical CSV file uploaded successfully.")
    else:
        history_data = pd.read_csv("machine_history.csv")
        st.info("Displaying the default sample historical data.")



except FileNotFoundError:
    st.warning(
        "Historical data is unavailable because "
        "machine_history.csv could not be found."
    )

except pd.errors.EmptyDataError:
    st.warning(
        "The machine_history.csv file is empty."
    )

except pd.errors.ParserError:
    st.warning(
        "The historical CSV file could not be read."
    )

else:
    history_required_columns = [
        "timestamp",
        "machine_id",
        "temperature",
        "vibration",
        "rpm",
        "torque",
        "operating_hours"
    ]

    history_missing_columns = [
        column
        for column in history_required_columns
        if column not in history_data.columns
    ]

    if history_missing_columns:
        st.error(
            "Historical data is missing these columns: "
            + ", ".join(history_missing_columns)
        )

    else:
        history_data["timestamp"] = pd.to_datetime(
            history_data["timestamp"],
            errors="coerce"
        )

        history_numeric_columns = [
            "temperature",
            "vibration",
            "rpm",
            "torque",
            "operating_hours"
        ]

        for column in history_numeric_columns:
            history_data[column] = pd.to_numeric(
                history_data[column],
                errors="coerce"
            )

        invalid_history_rows = history_data[
            history_data[
                ["timestamp"] + history_numeric_columns
            ].isnull().any(axis=1)
        ]

        if not invalid_history_rows.empty:
            st.error(
                "Some historical rows contain invalid timestamps "
                "or numerical readings."
            )

            st.dataframe(
                invalid_history_rows,
                use_container_width=True,
                hide_index=True
            )

        else:
            history_machine_column, history_sensor_column = (
                st.columns(2)
            )

            selected_history_machine = (
                history_machine_column.selectbox(
                    "Choose a machine for trend analysis",
                    options=sorted(
                        history_data["machine_id"].unique()
                    ),
                    key="history_machine_selector"
                )
            )

            history_sensor_options = {
                "Temperature (°C)": "temperature",
                "Vibration": "vibration",
                "RPM": "rpm",
                "Torque": "torque",
                "Operating Hours": "operating_hours"
            }

            selected_history_sensor_label = (
                history_sensor_column.selectbox(
                    "Choose a historical sensor",
                    options=list(
                        history_sensor_options.keys()
                    ),
                    key="history_sensor_selector"
                )
            )

            selected_history_sensor = history_sensor_options[
                selected_history_sensor_label
            ]

            selected_history_data = history_data[
                history_data["machine_id"]
                == selected_history_machine
            ].sort_values("timestamp")

            if selected_history_data.empty:
                st.warning(
                    "No historical readings are available "
                    "for the selected machine."
                )

            else:
                first_reading = selected_history_data[
                    selected_history_sensor
                ].iloc[0]

                latest_reading = selected_history_data[
                    selected_history_sensor
                ].iloc[-1]

                reading_change = (
                    latest_reading - first_reading
                )

                trend_metric1, trend_metric2, trend_metric3 = (
                    st.columns(3)
                )

                trend_metric1.metric(
                    "First Reading",
                    round(first_reading, 2)
                )

                trend_metric2.metric(
                    "Latest Reading",
                    round(latest_reading, 2)
                )

                trend_metric3.metric(
                    "Overall Change",
                    round(reading_change, 2)
                )

                trend_chart = px.line(
                    selected_history_data,
                    x="timestamp",
                    y=selected_history_sensor,
                    markers=True,
                    title=(
                        f"{selected_history_machine}: "
                        f"{selected_history_sensor_label} Over Time"
                    ),
                    labels={
                        "timestamp": "Time",
                        selected_history_sensor:
                            selected_history_sensor_label
                    }
                )

                st.plotly_chart(
                    trend_chart,
                    use_container_width=True
                )
                st.divider()

                st.subheader("ML-Based Anomaly Detection")

                st.write(
                    "Isolation Forest analyses all historical sensor readings "
                    "and identifies observations that differ unusually from "
                    "the overall data pattern."
                )

                anomaly_fraction = st.slider(
                    "Expected proportion of unusual readings",
                    min_value=0.05,
                    max_value=0.30,
                    value=0.15,
                    step=0.05,
                    format="%.2f",
                    help=(
                        "This controls approximately how many readings the model "
                        "will classify as anomalies."
                    )
                )

                anomaly_features = [
                    "temperature",
                    "vibration",
                    "rpm",
                    "torque",
                    "operating_hours"
                ]

                anomaly_results = detect_anomalies(
                    data=history_data,
                    feature_columns=anomaly_features,
                    contamination=anomaly_fraction
                )

                anomaly_count = (
                    anomaly_results["anomaly_status"] == "Anomaly"
                ).sum()

                normal_count = (
                    anomaly_results["anomaly_status"] == "Normal"
                ).sum()

                anomaly_metric1, anomaly_metric2, anomaly_metric3 = st.columns(3)

                anomaly_metric1.metric(
                    "Readings Analysed",
                    len(anomaly_results)
                )

                anomaly_metric2.metric(
                    "Normal Readings",
                    int(normal_count)
                )

                anomaly_metric3.metric(
                    "Anomalies Detected",
                    int(anomaly_count)
                )

                detected_anomalies = anomaly_results[
                    anomaly_results["anomaly_status"] == "Anomaly"
                ].sort_values(
                    by="anomaly_score",
                    ascending=False
                )

                st.markdown("#### Detected Anomalous Readings")

                if detected_anomalies.empty:
                    st.success(
                        "No unusual historical readings were detected."
                    )

                else:
                    st.warning(
                        f"{len(detected_anomalies)} unusual historical "
                        "reading(s) were detected."
                    )

                    st.dataframe(
                        detected_anomalies[
                            [
                                "timestamp",
                                "machine_id",
                                "temperature",
                                "vibration",
                                "rpm",
                                "torque",
                                "operating_hours",
                                "anomaly_score"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                anomaly_chart = px.scatter(
                    anomaly_results,
                    x="timestamp",
                    y="anomaly_score",
                    color="anomaly_status",
                    hover_data=[
                        "machine_id",
                        "temperature",
                        "vibration",
                        "rpm",
                        "torque",
                        "operating_hours"
                    ],
                    title="Historical Reading Anomaly Scores",
                    labels={
                        "timestamp": "Time",
                        "anomaly_score": "Anomaly Score",
                        "anomaly_status": "ML Classification"
                    }
                )

                st.plotly_chart(
                    anomaly_chart,
                    width="stretch"
                )

                st.caption(
                    "This model detects statistical outliers in the demonstration "
                    "dataset. It does not confirm mechanical failure or replace "
                    "professional inspection."
                )


# --------------------------------------------------
# INDIVIDUAL MACHINE INSPECTION
# --------------------------------------------------

st.subheader("Inspect Individual Machine")

selected_machine_id = st.selectbox(
    "Select a machine",
    filtered_data["machine_id"].tolist(),
    key="individual_machine_selector"
)

selected_machine = filtered_data[
    filtered_data["machine_id"] == selected_machine_id
].iloc[0]

risk_factors = identify_risk_factors(
    selected_machine
)

st.write(
    f"### {selected_machine_id} — "
    f"{selected_machine['health_status']}"
)


# --------------------------------------------------
# MACHINE DETAIL CARDS
# --------------------------------------------------

detail1, detail2, detail3 = st.columns(3)

detail1.metric(
    "Temperature",
    f"{selected_machine['temperature']} °C"
)

detail2.metric(
    "Vibration",
    selected_machine["vibration"]
)

detail3.metric(
    "RPM",
    int(selected_machine["rpm"])
)

detail4, detail5, detail6 = st.columns(3)

detail4.metric(
    "Torque",
    selected_machine["torque"]
)

detail5.metric(
    "Operating Hours",
    int(selected_machine["operating_hours"])
)

detail6.metric(
    "Risk Score",
    int(selected_machine["risk_score"])
)

st.markdown("#### Recommended Maintenance Action")

st.info(
    selected_machine["maintenance_action"]
)


# --------------------------------------------------
# HEALTH ASSESSMENT
# --------------------------------------------------

st.markdown("#### Health Assessment")

if selected_machine["health_status"] == "Critical":
    st.error(
        "This machine requires immediate inspection and should be "
        "prioritised before normal operation continues."
    )

elif selected_machine["health_status"] == "Warning":
    st.warning(
        "This machine should be monitored closely and scheduled for "
        "maintenance if abnormal readings continue."
    )

else:
    st.success(
        "This machine is operating within the selected normal range. "
        "Continue routine monitoring."
    )


st.markdown("#### Detected Risk Factors")

for reason in risk_factors:
    st.write(f"- {reason}")