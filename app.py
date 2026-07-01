import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Machine Health Dashboard",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Machine Health Monitoring Dashboard")

st.write(
    "Upload machine sensor data, compare multiple machines, "
    "identify abnormal operating conditions, and rank machines "
    "according to maintenance priority."
)

st.caption(
    "The thresholds used in this project are for educational and "
    "demonstration purposes only. They are not certified industrial limits."
)


# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------

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

except Exception as error:
    st.error(
        f"An unexpected error occurred while reading the file: {error}"
    )
    st.stop()


# ---------------------------------------------------------
# COLUMN VALIDATION
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# NUMERICAL DATA VALIDATION
# ---------------------------------------------------------

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

machine_data["machine_id"] = (
    machine_data["machine_id"]
    .astype(str)
    .str.strip()
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

blank_machine_ids = (
    machine_data["machine_id"].eq("")
    | machine_data["machine_id"].eq("nan")
)

if blank_machine_ids.any():
    st.error(
        "Some rows contain a missing machine ID."
    )

    st.dataframe(
        machine_data[blank_machine_ids],
        use_container_width=True,
        hide_index=True
    )

    st.stop()

if machine_data.empty:
    st.error(
        "The CSV file does not contain any machine records."
    )
    st.stop()

st.success("The machine data is valid.")


# ---------------------------------------------------------
# SIDEBAR THRESHOLD SETTINGS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# THRESHOLD VALIDATION
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# RISK CALCULATION FUNCTIONS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# APPLY RISK CALCULATIONS
# ---------------------------------------------------------

machine_data["risk_score"] = machine_data.apply(
    calculate_risk_score,
    axis=1
)

machine_data["health_status"] = machine_data[
    "risk_score"
].apply(assign_health_status)

ranked_data = machine_data.sort_values(
    by="risk_score",
    ascending=False
).reset_index(drop=True)


# ---------------------------------------------------------
# DASHBOARD SUMMARY
# ---------------------------------------------------------

st.divider()

st.subheader("Fleet Health Summary")

total_machines = len(ranked_data)

healthy_count = int(
    (ranked_data["health_status"] == "Healthy").sum()
)

warning_count = int(
    (ranked_data["health_status"] == "Warning").sum()
)

critical_count = int(
    (ranked_data["health_status"] == "Critical").sum()
)

column1, column2, column3, column4 = st.columns(4)

column1.metric(
    label="Total Machines",
    value=total_machines
)

column2.metric(
    label="Healthy",
    value=healthy_count
)

column3.metric(
    label="Warning",
    value=warning_count
)

column4.metric(
    label="Critical",
    value=critical_count
)


# ---------------------------------------------------------
# MACHINE RISK RANKING TABLE
# ---------------------------------------------------------

st.subheader("Machine Risk Ranking")

display_columns = [
    "machine_id",
    "temperature",
    "vibration",
    "rpm",
    "torque",
    "operating_hours",
    "risk_score",
    "health_status"
]

st.dataframe(
    ranked_data[display_columns],
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# RISK SCORE BAR CHART
# ---------------------------------------------------------

st.subheader("Risk Score Comparison")

risk_chart = px.bar(
    ranked_data,
    x="machine_id",
    y="risk_score",
    color="health_status",
    title="Machine Risk Scores",
    labels={
        "machine_id": "Machine",
        "risk_score": "Risk Score",
        "health_status": "Health Status"
    },
    category_orders={
        "health_status": [
            "Critical",
            "Warning",
            "Healthy"
        ]
    }
)

risk_chart.update_layout(
    xaxis_title="Machine",
    yaxis_title="Risk Score"
)

st.plotly_chart(
    risk_chart,
    use_container_width=True
)


# ---------------------------------------------------------
# INDIVIDUAL MACHINE INSPECTION
# ---------------------------------------------------------

st.divider()

st.subheader("Inspect Individual Machine")

selected_machine_id = st.selectbox(
    "Select a machine",
    ranked_data["machine_id"].tolist()
)

selected_machine = ranked_data[
    ranked_data["machine_id"] == selected_machine_id
].iloc[0]

risk_factors = identify_risk_factors(
    selected_machine
)

st.markdown(
    f"### {selected_machine_id} — "
    f"{selected_machine['health_status']}"
)

detail1, detail2, detail3 = st.columns(3)

detail1.metric(
    "Temperature",
    f"{selected_machine['temperature']:.1f} °C"
)

detail2.metric(
    "Vibration",
    f"{selected_machine['vibration']:.1f}"
)

detail3.metric(
    "RPM",
    f"{selected_machine['rpm']:.0f}"
)

detail4, detail5, detail6 = st.columns(3)

detail4.metric(
    "Torque",
    f"{selected_machine['torque']:.1f}"
)

detail5.metric(
    "Operating Hours",
    f"{selected_machine['operating_hours']:.0f}"
)

detail6.metric(
    "Risk Score",
    int(selected_machine["risk_score"])
)


# ---------------------------------------------------------
# HEALTH ASSESSMENT
# ---------------------------------------------------------

st.markdown("#### Health Assessment")

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
        "This machine is operating within the selected normal limits."
    )

st.markdown("#### Detected Risk Factors")

for reason in risk_factors:
    st.write(f"- {reason}")


# ---------------------------------------------------------
# CURRENT THRESHOLD SUMMARY
# ---------------------------------------------------------

with st.expander("View Current Risk Thresholds"):
    threshold_data = pd.DataFrame(
        {
            "Sensor": [
                "Temperature",
                "Vibration",
                "RPM",
                "Torque",
                "Operating Hours"
            ],
            "Warning Limit": [
                temperature_warning,
                vibration_warning,
                rpm_warning,
                torque_warning,
                hours_warning
            ],
            "Critical Limit": [
                temperature_critical,
                vibration_critical,
                rpm_critical,
                torque_critical,
                hours_critical
            ]
        }
    )

    st.dataframe(
        threshold_data,
        use_container_width=True,
        hide_index=True
    )