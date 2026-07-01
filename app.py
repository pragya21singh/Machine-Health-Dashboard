import pandas as pd
import plotly.express as px
import streamlit as st


# ==================================================
# PAGE SETTINGS
# ==================================================

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


# ==================================================
# FILE UPLOAD
# ==================================================

uploaded_file = st.file_uploader(
    "Upload machine data",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        machine_data = pd.read_csv(uploaded_file)

        st.success(
            "CSV file uploaded successfully."
        )

    else:
        machine_data = pd.read_csv(
            "machine_data.csv"
        )

        st.info(
            "Displaying the default sample machine data."
        )

except FileNotFoundError:
    st.error(
        "The default machine_data.csv file could not be found."
    )
    st.stop()

except pd.errors.EmptyDataError:
    st.error(
        "The uploaded CSV file is empty."
    )
    st.stop()

except pd.errors.ParserError:
    st.error(
        "The CSV file could not be read. Please check its format."
    )
    st.stop()


# ==================================================
# REQUIRED COLUMN VALIDATION
# ==================================================

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


# ==================================================
# NUMERICAL DATA VALIDATION
# ==================================================

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
    machine_data[numeric_columns]
    .isnull()
    .any(axis=1)
]

if not invalid_rows.empty:
    st.error(
        "Some rows contain missing or invalid numerical values."
    )

    st.write("Problematic rows:")

    st.dataframe(
        invalid_rows,
        width="stretch",
        hide_index=True
    )

    st.stop()

st.success(
    "The machine data is valid."
)


# ==================================================
# SIDEBAR THRESHOLD SETTINGS
# ==================================================

st.sidebar.header(
    "Risk Threshold Settings"
)

st.sidebar.caption(
    "Adjust the warning and critical limits used by the dashboard."
)


# Temperature thresholds

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


# Vibration thresholds

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


# RPM thresholds

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


# Torque thresholds

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


# Operating-hour thresholds

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


# ==================================================
# THRESHOLD VALIDATION
# ==================================================

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


# ==================================================
# RISK CALCULATION FUNCTIONS
# ==================================================

def calculate_risk_score(row):
    """Calculate the total risk score for one machine."""

    score = 0

    # Temperature risk

    if row["temperature"] > temperature_critical:
        score += 3

    elif row["temperature"] > temperature_warning:
        score += 1


    # Vibration risk

    if row["vibration"] > vibration_critical:
        score += 3

    elif row["vibration"] > vibration_warning:
        score += 1


    # RPM risk

    if row["rpm"] > rpm_critical:
        score += 3

    elif row["rpm"] > rpm_warning:
        score += 1


    # Torque risk

    if row["torque"] > torque_critical:
        score += 3

    elif row["torque"] > torque_warning:
        score += 1


    # Operating-hours risk

    if row["operating_hours"] > hours_critical:
        score += 3

    elif row["operating_hours"] > hours_warning:
        score += 1

    return score


def assign_health_status(score):
    """Convert a risk score into a health category."""

    if score >= 8:
        return "Critical"

    elif score >= 4:
        return "Warning"

    else:
        return "Healthy"


def identify_risk_factors(row):
    """Explain why a machine received its risk score."""

    reasons = []

    # Temperature explanation

    if row["temperature"] > temperature_critical:
        reasons.append(
            "Temperature exceeds the critical limit"
        )

    elif row["temperature"] > temperature_warning:
        reasons.append(
            "Temperature exceeds the warning limit"
        )


    # Vibration explanation

    if row["vibration"] > vibration_critical:
        reasons.append(
            "Vibration exceeds the critical limit"
        )

    elif row["vibration"] > vibration_warning:
        reasons.append(
            "Vibration exceeds the warning limit"
        )


    # RPM explanation

    if row["rpm"] > rpm_critical:
        reasons.append(
            "RPM exceeds the critical limit"
        )

    elif row["rpm"] > rpm_warning:
        reasons.append(
            "RPM exceeds the warning limit"
        )


    # Torque explanation

    if row["torque"] > torque_critical:
        reasons.append(
            "Torque exceeds the critical limit"
        )

    elif row["torque"] > torque_warning:
        reasons.append(
            "Torque exceeds the warning limit"
        )


    # Operating-hours explanation

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


# ==================================================
# CALCULATE MACHINE HEALTH
# ==================================================

machine_data["risk_score"] = machine_data.apply(
    calculate_risk_score,
    axis=1
)

machine_data["health_status"] = machine_data[
    "risk_score"
].apply(
    assign_health_status
)

ranked_data = machine_data.sort_values(
    by="risk_score",
    ascending=False
).reset_index(drop=True)


# ==================================================
# SIDEBAR STATUS FILTER
# ==================================================

st.sidebar.divider()

st.sidebar.subheader(
    "Dashboard Filters"
)

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
    ranked_data["health_status"].isin(
        selected_statuses
    )
].copy()

if filtered_data.empty:
    st.warning(
        "No machines match the selected health-status filter."
    )
    st.stop()


# ==================================================
# DASHBOARD SUMMARY CARDS
# ==================================================

total_machines = len(
    filtered_data
)

healthy_count = (
    filtered_data["health_status"] == "Healthy"
).sum()

warning_count = (
    filtered_data["health_status"] == "Warning"
).sum()

critical_count = (
    filtered_data["health_status"] == "Critical"
).sum()


summary_column1, summary_column2, summary_column3, summary_column4 = (
    st.columns(4)
)

summary_column1.metric(
    label="Total Machines",
    value=total_machines
)

summary_column2.metric(
    label="Healthy",
    value=int(healthy_count)
)

summary_column3.metric(
    label="Warning",
    value=int(warning_count)
)

summary_column4.metric(
    label="Critical",
    value=int(critical_count)
)


# ==================================================
# MACHINE RISK TABLE
# ==================================================

st.subheader(
    "Machine Risk Ranking"
)

st.dataframe(
    filtered_data,
    width="stretch",
    hide_index=True
)


# ==================================================
# DOWNLOADABLE MACHINE REPORT
# ==================================================

report_csv = filtered_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Machine Report",
    data=report_csv,
    file_name="machine_health_report.csv",
    mime="text/csv",
    icon=":material/download:",
    width="stretch",
    on_click="ignore"
)


# ==================================================
# MACHINE RISK-SCORE CHART
# ==================================================

st.subheader(
    "Risk Score Comparison"
)

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
    },
    hover_data={
        "temperature": True,
        "vibration": True,
        "rpm": True,
        "torque": True,
        "operating_hours": True
    }
)

st.plotly_chart(
    risk_chart,
    width="stretch"
)


# ==================================================
# SENSOR COMPARISON EXPLORER
# ==================================================

st.subheader(
    "Sensor Comparison Explorer"
)

sensor_options = {
    "Temperature (°C)": "temperature",
    "Vibration": "vibration",
    "RPM": "rpm",
    "Torque": "torque",
    "Operating Hours": "operating_hours"
}

selected_sensor_label = st.selectbox(
    "Choose a sensor parameter to compare",
    options=list(sensor_options.keys())
)

selected_sensor_column = sensor_options[
    selected_sensor_label
]

sensor_data = filtered_data.sort_values(
    by=selected_sensor_column,
    ascending=False
).copy()

sensor_average = sensor_data[
    selected_sensor_column
].mean()

highest_sensor_index = sensor_data[
    selected_sensor_column
].idxmax()

highest_sensor_row = sensor_data.loc[
    highest_sensor_index
]


sensor_summary1, sensor_summary2 = st.columns(2)

sensor_summary1.metric(
    label=f"Average {selected_sensor_label}",
    value=round(sensor_average, 2)
)

sensor_summary2.metric(
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
        "risk_score": True,
        "health_status": True
    }
)

st.plotly_chart(
    sensor_chart,
    width="stretch"
)


# ==================================================
# INDIVIDUAL MACHINE INSPECTION
# ==================================================

st.subheader(
    "Inspect Individual Machine"
)

selected_machine_id = st.selectbox(
    "Select a machine",
    filtered_data["machine_id"].tolist()
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


# First row of readings

detail1, detail2, detail3 = st.columns(3)

detail1.metric(
    label="Temperature",
    value=f"{selected_machine['temperature']} °C"
)

detail2.metric(
    label="Vibration",
    value=selected_machine["vibration"]
)

detail3.metric(
    label="RPM",
    value=int(selected_machine["rpm"])
)


# Second row of readings

detail4, detail5, detail6 = st.columns(3)

detail4.metric(
    label="Torque",
    value=selected_machine["torque"]
)

detail5.metric(
    label="Operating Hours",
    value=int(
        selected_machine["operating_hours"]
    )
)

detail6.metric(
    label="Risk Score",
    value=int(
        selected_machine["risk_score"]
    )
)


# ==================================================
# HEALTH ASSESSMENT
# ==================================================

st.markdown(
    "#### Health Assessment"
)

if selected_machine["health_status"] == "Critical":
    st.error(
        "This machine requires immediate inspection."
    )

elif selected_machine["health_status"] == "Warning":
    st.warning(
        "This machine should be monitored and inspected soon."
    )

else:
    st.success(
        "This machine is operating within the selected normal range."
    )


st.markdown(
    "#### Detected Risk Factors"
)

for reason in risk_factors:
    st.write(
        f"- {reason}"
    )