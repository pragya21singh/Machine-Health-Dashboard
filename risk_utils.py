def calculate_risk_score(row, thresholds):
    score = 0

    if row["temperature"] > thresholds["temperature_critical"]:
        score += 3
    elif row["temperature"] > thresholds["temperature_warning"]:
        score += 1

    if row["vibration"] > thresholds["vibration_critical"]:
        score += 3
    elif row["vibration"] > thresholds["vibration_warning"]:
        score += 1

    if row["rpm"] > thresholds["rpm_critical"]:
        score += 3
    elif row["rpm"] > thresholds["rpm_warning"]:
        score += 1

    if row["torque"] > thresholds["torque_critical"]:
        score += 3
    elif row["torque"] > thresholds["torque_warning"]:
        score += 1

    if row["operating_hours"] > thresholds["hours_critical"]:
        score += 3
    elif row["operating_hours"] > thresholds["hours_warning"]:
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


def identify_risk_factors(row, thresholds):
    reasons = []

    if row["temperature"] > thresholds["temperature_critical"]:
        reasons.append("Temperature exceeds the critical limit")
    elif row["temperature"] > thresholds["temperature_warning"]:
        reasons.append("Temperature exceeds the warning limit")

    if row["vibration"] > thresholds["vibration_critical"]:
        reasons.append("Vibration exceeds the critical limit")
    elif row["vibration"] > thresholds["vibration_warning"]:
        reasons.append("Vibration exceeds the warning limit")

    if row["rpm"] > thresholds["rpm_critical"]:
        reasons.append("RPM exceeds the critical limit")
    elif row["rpm"] > thresholds["rpm_warning"]:
        reasons.append("RPM exceeds the warning limit")

    if row["torque"] > thresholds["torque_critical"]:
        reasons.append("Torque exceeds the critical limit")
    elif row["torque"] > thresholds["torque_warning"]:
        reasons.append("Torque exceeds the warning limit")

    if row["operating_hours"] > thresholds["hours_critical"]:
        reasons.append("Operating hours exceed the critical maintenance limit")
    elif row["operating_hours"] > thresholds["hours_warning"]:
        reasons.append("Operating hours exceed the warning maintenance limit")

    if not reasons:
        reasons.append("All readings are within the selected operating limits")

    return reasons