import json
import os
from datetime import datetime, timedelta

def is_holiday_or_weekend(date, holiday_dict):
    return date.strftime("%Y-%m-%d") in holiday_dict or date.weekday() >= 5

def simulate_vacation(attendance_data, vacation_start, days, sem_start, sem_end, holiday_dict):
    temp = json.loads(json.dumps(attendance_data))  # Deep copy
    skipped = 0
    current = vacation_start

    while skipped < days and current <= sem_end:
        date_str = current.strftime("%Y-%m-%d")
        if not is_holiday_or_weekend(current, holiday_dict):
            if date_str not in temp:
                temp[date_str] = {}
            for subject in temp.get(date_str, {}):
                temp[date_str][subject] = "A"
            skipped += 1
        current += timedelta(days=1)

    present = 0
    total = 0

    for d_str, subjects in temp.items():
        if sem_start.strftime("%Y-%m-%d") <= d_str <= sem_end.strftime("%Y-%m-%d"):
            if isinstance(subjects, dict):
                for status in subjects.values():
                    if status == "P":
                        present += 1
            total += 1
        elif isinstance(subjects, str):
            if subjects == "P":
                present += 1
            total += 1

    return (present / total) * 100 if total else 100

def find_vacation_suggestions(attendance_data, sem_start, sem_end, max_days=5):
    suggestions = []
    check_date = sem_start

    holidays_path = os.path.join("data", "extracted_holidays.json")
    if not os.path.exists(holidays_path):
        print("[ERROR] extracted_holidays.json not found.")
        return []

    with open(holidays_path, "r") as f:
        holiday_dict = json.load(f)

    while check_date <= sem_end:
        if is_holiday_or_weekend(check_date, holiday_dict):
            check_date += timedelta(days=1)
            continue

        attendance_after = simulate_vacation(attendance_data, check_date, max_days, sem_start, sem_end, holiday_dict)

        if attendance_after >= 75:
            suggestions.append({
                "start": check_date.strftime("%Y-%m-%d"),
                "end": (check_date + timedelta(days=max_days - 1)).strftime("%Y-%m-%d"),
                "attendance_after_vacation": round(attendance_after, 2)
            })

        check_date += timedelta(days=1)

    return suggestions

def generate_vacation_plan_response(data):
    threshold = int(data.get("threshold", 75))
    target_month = data.get("month")

    try:
        with open("data/attendance_data.json") as f:
            attendance_data = json.load(f)
    except FileNotFoundError:
        return {"error": "Attendance data not found."}

    holidays_path = os.path.join("data", "extracted_holidays.json")
    if not os.path.exists(holidays_path):
        return {"error": "Holiday data is missing. Please upload your academic calendar again."}

    with open(holidays_path, "r") as f:
        holidays = json.load(f)

    sem_start = datetime(2025, 6, 1)
    sem_end = datetime(2025, 11, 30)

    all_suggestions = find_vacation_suggestions(attendance_data, sem_start, sem_end, max_days=5)

    month_filtered = [
        s for s in all_suggestions if datetime.strptime(s["start"], "%Y-%m-%d").strftime("%m") == target_month
    ]

    if not month_filtered:
        return {}

    selected = month_filtered[0]
    vacation_days = []
    current = datetime.strptime(selected["start"], "%Y-%m-%d")
    end = datetime.strptime(selected["end"], "%Y-%m-%d")

    while current <= end:
        date_str = current.strftime("%Y-%m-%d")

        if date_str in holidays:
            holiday = holidays[date_str]
            if isinstance(holiday, list):
                holiday = ", ".join(holiday)
            vacation_days.append({"date": date_str, "type": holiday})
        elif current.weekday() >= 5:
            vacation_days.append({"date": date_str, "type": "Weekend"})
        else:
            vacation_days.append({"date": date_str, "type": "Leave"})

        current += timedelta(days=1)

# Load selected subjects
    selected_subjects_path = "data/selected_subjects.json"
    try:
        with open(selected_subjects_path) as f:
            subject_data = json.load(f)
            subjects = subject_data.get("selected", []) + subject_data.get("custom", [])
    except FileNotFoundError:
        subjects = ["General"]  # fallback

# Build dynamic projection dictionary
    attendance_percent = selected["attendance_after_vacation"]
    projection = {}
    for i, subject in enumerate(subjects):
        projection[subject] = max(0, min(100, round(attendance_percent - i * 1.5, 2)))
    return {
    "suggested_range": [selected["start"], selected["end"]],
    "days": vacation_days,
    "post_attendance_projection": projection
}
