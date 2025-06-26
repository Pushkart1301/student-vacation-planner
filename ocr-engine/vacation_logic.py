# vacation_logic.py
import json
import os
from datetime import datetime, timedelta


def find_vacation_suggestions(attendance_data, sem_start, sem_end, max_days=5):
    suggestions = []
    check_date = sem_start

    def is_holiday_or_weekend(date, holiday_dict):
        return date.strftime("%Y-%m-%d") in holiday_dict or date.weekday() >= 5

    def simulate_vacation(attendance_data, vacation_start, days, sem_start, sem_end, holiday_dict):
        temp = attendance_data.copy()
        skipped = 0
        current = vacation_start
        while skipped < days and current <= sem_end:
            if not is_holiday_or_weekend(current, holiday_dict):
                temp[current.strftime("%Y-%m-%d")] = "absent"
                skipped += 1
            current += timedelta(days=1)

        present = sum(
            1 for d in temp
            if sem_start.strftime("%Y-%m-%d") <= d <= sem_end.strftime("%Y-%m-%d") and temp[d] == "present"
        )
        total = sum(
            1 for d in temp
            if sem_start.strftime("%Y-%m-%d") <= d <= sem_end.strftime("%Y-%m-%d")
        )
        return (present / total) * 100 if total else 100

    holidays_path = os.path.join("data", "extracted_holidays.json")
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
    target_month = data.get("month")  # e.g., "08" for August

    # Load data
    attendance_data = json.load(open("data/attendance_data.json"))
    holidays = json.load(open("data/extracted_holidays.json"))

    sem_start = datetime(2025, 7, 1)
    sem_end = datetime(2025, 11, 30)

    all_suggestions = find_vacation_suggestions(attendance_data, sem_start, sem_end, max_days=5)

    # Filter for the selected month
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
            vacation_days.append({"date": date_str, "type": "Holiday"})
        elif current.weekday() >= 5:
            vacation_days.append({"date": date_str, "type": "Weekend"})
        else:
            vacation_days.append({"date": date_str, "type": "Leave"})
        current += timedelta(days=1)

    return {
        "suggested_range": [selected["start"], selected["end"]],
        "days": vacation_days,
        "post_attendance_projection": {
            "Mathematics": selected["attendance_after_vacation"],
            "Physics": selected["attendance_after_vacation"] - 2,
            "Chemistry": selected["attendance_after_vacation"] - 4,
        }
    }
