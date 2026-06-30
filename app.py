import pandas as pd
import plotly.express as px
import streamlit as st


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="Machine Health Dashboard",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Machine Health Monitoring Dashboard")

st.write(
    "This dashboard compares multiple machines using temperature, "
    "vibration, RPM, torque, and operating hours."
)


# -----------------------------
# Risk calculation functions
# -----------------------------

def calculate_risk_score(row):
    score = 0

    # Temperature risk
    if row["temperature"] > 100:
        score += 3
    elif row["temperature"] > 85:
        score += 2
    elif row["temperature"] > 75:
        score += 1

    # Vibration risk
    if row["vibration"] > 6:
        score += 3
    elif row["vibration"] > 4:
        score += 2
    elif row["vibration"] > 3:
        score += 1

    # RPM risk
    if row["rpm"] > 1650:
        score += 2
    elif row["rpm"] > 1550:
        score += 1

    # Torque risk
    if row["torque"] > 45:
        score += 2
    elif row["torque"] > 38:
        score += 1

    # Operating-hours risk
    if row["operating_hours"] > 1000:
        score += 2
    elif row["operating_hours"] > 700:
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

    # Temperature explanation
    if row["temperature"] > 100:
        reasons.append("Temperature is extremely high")
    elif row["temperature"] > 85:
        reasons.append("Temperature is high")
    elif row["temperature"] > 75:
        reasons.append("Temperature is slightly elevated")

    # Vibration explanation
    if row["vibration"] > 6:
        reasons.append("Vibration is extremely high")
    elif row["vibration"] > 4:
        reasons.append("Vibration is high")
    elif row["vibration"] > 3:
        reasons.append("Vibration is slightly elevated")

    # RPM explanation
    if row["rpm"] > 1650:
        reasons.append("RPM is extremely high")
    elif row["rpm"] > 1550:
        reasons.append("RPM is high")

    # Torque explanation
    if row["torque"] > 45:
        reasons.append("Torque is extremely high")
    elif row["torque"] > 38:
        reasons.append("Torque is high")

    # Operating-hours explanation
    if row["operating_hours"] > 1000:
        reasons.append("Machine has very high operating hours")
    elif row["operating_hours"] > 700:
        reasons.append("Machine may require scheduled maintenance")

    if not reasons:
        reasons.append(
            "All readings are within the defined normal range"
        )

    return reasons


# -----------------------------
# File upload
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload machine data",
    type=["csv"]
)


try:
    # Use uploaded data if available.
    if uploaded_file is not None:
        machine_data = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully.")

    # Otherwise, use the default sample file.
    else:
        machine_data = pd.read_csv("machine_data.csv")
        st.info("Displaying the default sample machine data.")

    # -----------------------------
    # Column validation
    # -----------------------------

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

    else:
        # -----------------------------
        # Numeric-value validation
        # -----------------------------

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

        else:
            st.success("The machine data is valid.")

            # -----------------------------
            # Calculate risk scores
            # -----------------------------

            machine_data["risk_score"] = machine_data.apply(
                calculate_risk_score,
                axis=1
            )

            machine_data["health_status"] = (
                machine_data["risk_score"].apply(
                    assign_health_status
                )
            )

            ranked_data = machine_data.sort_values(
                by="risk_score",
                ascending=False
            )

            # -----------------------------
            # Dashboard summary cards
            # -----------------------------

            total_machines = len(ranked_data)

            healthy_count = (
                ranked_data["health_status"] == "Healthy"
            ).sum()

            warning_count = (
                ranked_data["health_status"] == "Warning"
            ).sum()

            critical_count = (
                ranked_data["health_status"] == "Critical"
            ).sum()

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

            # -----------------------------
            # Machine ranking table
            # -----------------------------

            st.subheader("Machine Risk Ranking")

            st.dataframe(
                ranked_data,
                use_container_width=True,
                hide_index=True
            )

            # -----------------------------
            # Risk-score chart
            # -----------------------------

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
                }
            )

            st.plotly_chart(
                risk_chart,
                use_container_width=True
            )

            # -----------------------------
            # Individual machine inspection
            # -----------------------------

            st.subheader("Inspect Individual Machine")

            selected_machine_id = st.selectbox(
                "Select a machine",
                ranked_data["machine_id"].tolist()
            )

            selected_machine = ranked_data[
                ranked_data["machine_id"]
                == selected_machine_id
            ].iloc[0]

            risk_factors = identify_risk_factors(
                selected_machine
            )

            st.write(
                f"### {selected_machine_id} — "
                f"{selected_machine['health_status']}"
            )

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

            # -----------------------------
            # Health explanation
            # -----------------------------

            st.markdown("#### Health Assessment")

            if selected_machine["health_status"] == "Critical":
                st.error(
                    "This machine requires immediate inspection."
                )

            elif selected_machine["health_status"] == "Warning":
                st.warning(
                    "This machine should be monitored "
                    "and inspected soon."
                )

            else:
                st.success(
                    "This machine is operating within "
                    "the defined normal range."
                )

            st.markdown("#### Detected Risk Factors")

            for reason in risk_factors:
                st.write(f"- {reason}")


except FileNotFoundError:
    st.error(
        "The default machine_data.csv file could not be found."
    )

except pd.errors.EmptyDataError:
    st.error(
        "The uploaded CSV file is empty."
    )

except pd.errors.ParserError:
    st.error(
        "The CSV file could not be read. "
        "Please check its format."
    )
