import json
import os
from datetime import datetime, timedelta
from groq_module import get_vacation_plan_from_groq
import re

def parse_groq_json(content):
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON object found in Groq response")
    return json.loads(match.group(0))


def is_holiday_or_weekend(date, holiday_dict):
    return date.strftime("%Y-%m-%d") in holiday_dict or date.weekday() >= 5

def calculate_subject_wise_summary(attendance_data, subjects, sem_start, sem_end):
    subject_summary = {subj: {"P": 0, "A": 0} for subj in subjects}

    for date_str, records in attendance_data.items():
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            continue
        if not (sem_start <= date <= sem_end):
            continue
        for subject, status in records.items():
            if subject in subject_summary:
                if status == "P":
                    subject_summary[subject]["P"] += 1
                elif status == "A":
                    subject_summary[subject]["A"] += 1

    percent_summary = {}
    for subj, stats in subject_summary.items():
        total = stats["P"] + stats["A"]
        percent = (stats["P"] / total * 100) if total else 100
        percent_summary[subj] = round(percent, 2)
    return percent_summary

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

    # Load attendance
    try:
        with open("data/attendance_data.json") as f:
            attendance_data = json.load(f)
    except FileNotFoundError:
        return {"error": "Attendance data not found."}

    # Load holidays
    holidays_path = os.path.join("data", "extracted_holidays.json")
    if not os.path.exists(holidays_path):
        return {"error": "Holiday data is missing. Please upload your academic calendar again."}

    with open(holidays_path, "r") as f:
        holiday_data = json.load(f)

    sem_start = datetime(2025, 6, 1)
    sem_end = datetime(2025, 11, 30)

    # Load subjects
    selected_subjects_path = "data/selected_subjects.json"
    try:
        with open(selected_subjects_path) as f:
            subject_data = json.load(f)
            subjects = subject_data.get("selected", []) + subject_data.get("custom", [])
    except FileNotFoundError:
        subjects = ["General"]

    # ➕ Subject-wise attendance summary
    subject_summary = calculate_subject_wise_summary(attendance_data, subjects, sem_start, sem_end)

    # 🔍 Try Groq-based planning
    try:
        groq_result = get_vacation_plan_from_groq(
            attendance_summary=subject_summary,
            holidays=holiday_data,
            semester_start=sem_start.strftime("%Y-%m-%d"),
            semester_end=sem_end.strftime("%Y-%m-%d"),
            threshold=threshold,
            preferred_month=target_month
        )

        if groq_result and "suggested_range" in groq_result:
            start_str, end_str = groq_result["suggested_range"]
            current = datetime.strptime(start_str, "%Y-%m-%d")
            end = datetime.strptime(end_str, "%Y-%m-%d")
            vacation_days = []

            while current <= end:
                d_str = current.strftime("%Y-%m-%d")
                if d_str in holiday_data:
                    h = holiday_data[d_str]
                    h = ", ".join(h) if isinstance(h, list) else h
                    vacation_days.append({"date": d_str, "type": h})
                elif current.weekday() >= 5:
                    vacation_days.append({"date": d_str, "type": "Weekend"})
                else:
                    vacation_days.append({"date": d_str, "type": "Leave"})
                current += timedelta(days=1)

            return {
                "suggested_range": groq_result["suggested_range"],
                "days": vacation_days,
                "post_attendance_projection": groq_result.get("projected_attendance", {})
            }
    except Exception as e:
        print("[Groq ERROR]", e)

    # 🔁 Fallback to local suggestion
    print("[INFO] Falling back to local planner")
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
        if date_str in holiday_data:
            holiday = holiday_data[date_str]
            if isinstance(holiday, list):
                holiday = ", ".join(holiday)
            vacation_days.append({"date": date_str, "type": holiday})
        elif current.weekday() >= 5:
            vacation_days.append({"date": date_str, "type": "Weekend"})
        else:
            vacation_days.append({"date": date_str, "type": "Leave"})
        current += timedelta(days=1)

    # Estimate per-subject projection for fallback
    attendance_percent = selected["attendance_after_vacation"]
    projection = {}
    for i, subject in enumerate(subjects):
        projection[subject] = max(0, min(100, round(attendance_percent - i * 1.5, 2)))

    return {
        "suggested_range": [selected["start"], selected["end"]],
        "days": vacation_days,
        "post_attendance_projection": projection
    }
