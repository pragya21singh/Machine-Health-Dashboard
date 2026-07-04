# Machine Health Monitoring Dashboard
## Live Demo

[Open the Machine Health Dashboard](https://zuaycz2u5vt9crg82xcavj.streamlit.app/)

An interactive Python and Streamlit dashboard that compares multiple machines, identifies abnormal operating conditions, calculates risk scores, and ranks machines according to maintenance priority.

## Project Overview

This project is an interactive machine health monitoring dashboard built using Python and Streamlit. It is designed to help compare multiple machines, identify abnormal operating conditions, analyse historical sensor trends, and detect unusual readings using basic machine learning.

The project connects mechanical engineering context with software development, data analysis, and machine learning.

## Features

* Upload machine data using a CSV file
* Validate required columns and numerical values
* Calculate a rule-based risk score for each machine
* Classify machines as Healthy, Warning, or Critical
* Rank machines from highest to lowest risk
* Display dashboard summary metrics
* Compare machine risk scores using an interactive chart
* Inspect individual machine readings
* Explain the factors contributing to each machine’s health status
* Analyse historical sensor trends over time
* Detect unusual sensor readings using Isolation Forest anomaly detection
* Visualise anomaly scores using an interactive scatter plot

## Workflow

1. The user uploads machine sensor data in CSV format.
2. The dashboard validates the file structure and numerical readings.
3. Each machine receives a rule-based risk score.
4. Machines are classified as Healthy, Warning, or Critical.
5. The user can adjust risk thresholds from the sidebar.
6. The dashboard displays rankings, charts, and maintenance recommendations.
7. Historical sensor data can be analysed over time.
8. Isolation Forest is used to detect unusual historical readings.
9. Reports can be downloaded as CSV files.

## Technologies Used

* Python
* Streamlit
* Pandas
* Plotly
* Scikit-learn

## Required CSV Format

The uploaded CSV file must contain the following columns:

* `machine_id`
* `temperature`
* `vibration`
* `rpm`
* `torque`
* `operating_hours`

Example:

```csv
machine_id,temperature,vibration,rpm,torque,operating_hours
M001,68,2.1,1450,32,420
M002,91,5.8,1600,41,870
M003,74,3.2,1520,35,610
```

## Run the Project Locally

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/machine-health-dashboard.git
```

Move into the project folder:

```bash
cd machine-health-dashboard
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

Start the Streamlit application:

```bash
streamlit run app.py
```

## How the Risk Score Works

The dashboard assigns points when readings such as temperature, vibration, RPM, torque, or operating hours exceed predefined demonstration thresholds.

The total score is converted into one of three health categories:

* Healthy: Risk score from 0 to 3
* Warning: Risk score from 4 to 7
* Critical: Risk score of 8 or more

## Important Note

The risk thresholds used in this project are created for educational and demonstration purposes. They are not certified industrial safety or maintenance limits.
The anomaly-detection model identifies statistical outliers in the demonstration dataset. It does not confirm actual mechanical failure and should not be treated as a replacement for professional inspection.

## What I Learned

Through this project, I learned how to:

- Build an interactive web dashboard using Streamlit
- Work with CSV data using Pandas
- Validate uploaded data before processing
- Create interactive charts using Plotly
- Design a rule-based risk scoring system
- Analyse historical sensor trends
- Apply Isolation Forest for anomaly detection
- Organise code using separate utility files
- Deploy a Python application publicly
- Document a software project for GitHub

## Limitations

- The sensor thresholds are demonstration values, not certified industrial safety limits.
- The sample datasets are educational and not collected from real machines.
- The anomaly detection model identifies statistical outliers, not confirmed mechanical failures.
- The project does not currently include real-time sensor integration.

## Future Improvements

* Add time-series sensor data
* Introduce anomaly detection
* Add machine-failure prediction using machine learning
* Allow users to configure safe operating thresholds
* Generate downloadable maintenance reports
* Deploy the dashboard publicly

## Author

Mechanical engineering student exploring software development, data analysis, and machine learning through industrial applications.
