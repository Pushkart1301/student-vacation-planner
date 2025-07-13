from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask import Flask, request, jsonify, render_template
from vacation_logic import calculate_subject_wise_summary
from groq_module import ( extract_holidays_from_groq, get_vacation_plan_from_groq, ask_groq_chatbot)
from flask_cors import CORS
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import pytesseract
from pdf2image import convert_from_bytes
import pdfplumber
import io
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
try:
    from groq_module_private import extract_holidays_from_groq
except ImportError:
    from groq_module import extract_holidays_from_groq

app = Flask(__name__)
CORS(app)

# Update your static holiday planner
HOLIDAYS = []  # Will be filled by uploaded calendar
USER_THRESHOLD = 75

# Mock timetable data parsed from your uploaded PDF (can be updated dynamically later)
timetable = {
    "Monday": ["DBMS", "BAI", "MATHS"],
    "Tuesday": ["DBMS", "CN", "BAI"],
    "Wednesday": ["CN", "DBMS", "MATHS"],
    "Thursday": ["BAI", "MATHS", "PS-III"],
    "Friday": ["DBMS", "CN", "BAI"],
    "Saturday": ["PROJECT", "ACTIVITY"],
    "Sunday": []
}

attendance_data = {}

attendance_data_file = "data/attendance_data.json"
if os.path.exists(attendance_data_file) and os.path.getsize(attendance_data_file) > 0:
    with open(attendance_data_file) as f:
        attendance_data = json.load(f)



@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/save-lecture-schedule', methods=['POST'])
def save_lecture_schedule():
    data = request.get_json()
    try:
        with open("data/lecture_schedule.json", "w") as f:
            json.dump(data, f, indent=2)
        return jsonify({"status": "success", "message": "Lecture schedule saved successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

from datetime import datetime


@app.route('/holiday-results')
def show_extracted_holidays():
    holidays_path = "data/extracted_holidays.json"
    if not os.path.exists(holidays_path):
        return "No holiday data found. Please upload your academic calendar.", 404

    with open(holidays_path) as f:
        holiday_data = json.load(f)

    # ✅ If it's an error dict, show message instead of crashing
    if isinstance(holiday_data, dict) and "error" in holiday_data:
        return f"❌ Failed to extract holidays: {holiday_data['error']}", 500

    holidays = []
    for h in holiday_data:
        if not isinstance(h, dict):
            print("[WARNING] Skipping non-dict entry:", h)
            continue
        try:
            date_obj = datetime.strptime(h["date"], "%d %B %Y")
            holidays.append({
                "date": h["date"],
                "event": h["event"],
                "weekday": h.get("weekday", date_obj.strftime("%A"))
            })
        except Exception as e:
            print("[ERROR] Skipping invalid holiday entry:", h, "| Error:", str(e))

    holidays.sort(key=lambda x: datetime.strptime(x["date"], "%d %B %Y"))

    return render_template("holiday_results.html", holidays=holidays)


@app.route('/api/lectures-for-date/<date>', methods=['GET'])
def lectures_for_date(date):
    try:
        with open("data/lecture_mapping.json") as f:
            lecture_schedule = json.load(f)

        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
        subjects = lecture_schedule.get(weekday, [])

        return jsonify({"weekday": weekday, "lectures": subjects})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/get-lecture-schedule')
def get_lecture_schedule():
    try:
        with open("data/lecture_schedule.json") as f:
            schedule = json.load(f)
        return jsonify(schedule)
    except FileNotFoundError:
        return jsonify({})

@app.route('/map-lectures', methods=['GET', 'POST'])
def map_lectures():
    mapping_file = "data/lecture_mapping.json"
    selected_subjects_file = "data/selected_subjects.json"

    if os.path.exists(selected_subjects_file):
        with open(selected_subjects_file) as f:
            subjects_data = json.load(f)
            subjects = subjects_data.get("selected", []) + subjects_data.get("custom", [])
    else:
        subjects = []

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    if request.method == 'POST':
        mapping = {}
        for day in weekdays:
            mapping[day] = request.form.getlist(day)
        with open(mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)
        return redirect(url_for('dashboard'))

    saved_mapping = {}
    if os.path.exists(mapping_file):
        with open(mapping_file) as f:
            saved_mapping = json.load(f)

    return render_template("map_lectures.html", subjects=subjects, weekdays=weekdays, saved_mapping=saved_mapping)



selected_subjects_file = "data/selected_subjects.json"  # make sure this folder exists
if not os.path.exists("data"):
    os.makedirs("data")

@app.route('/save-subjects', methods=['POST'])
def save_subjects():
    data = request.get_json()
    
    # ✅ Save selected subjects
    with open("data/selected_subjects.json", "w") as f:
        json.dump(data, f, indent=2)
    
    # ✅ Reset lecture schedule to match new subjects
    lecture_schedule_path = "data/lecture_schedule.json"
    if os.path.exists(lecture_schedule_path):
        os.remove(lecture_schedule_path)  # Delete old schedule

    return jsonify({"status": "success"})


@app.route('/get-selected-subjects')
def get_selected_subjects():
    try:
        with open("data/selected_subjects.json") as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({"selected": []})
@app.route('/select-subjects')
def select_subjects():
    return render_template('subject_selection.html')


@app.route('/upload')
def upload_form():
    return render_template('test_form.html')

@app.route('/attendance')
def attendance_ui():
    try:
        with open("data/lecture_schedule.json") as f:
            lecture_schedule = json.load(f)
    except FileNotFoundError:
        lecture_schedule = {}

    return render_template("attendance.html", lecture_schedule=lecture_schedule)


@app.route('/api/get-timetable/<date>', methods=['GET'])
def get_timetable(date):
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        weekday = dt.strftime("%A")
        return jsonify({"date": date, "day": weekday, "lectures": timetable.get(weekday, [])})
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

@app.route('/api/mark-attendance', methods=['POST'])
def mark_attendance():
    global attendance_data

    data = request.json
    date = data.get("date")
    subject = data.get("subject")
    status = data.get("status")  # 'P' or 'A'

    if not all([date, subject, status]):
        return jsonify({"error": "Missing required fields."}), 400

    # Initialize date if not present
    if date not in attendance_data:
        attendance_data[date] = {}

    attendance_data[date][subject] = status

    # Save to JSON
    with open("data/attendance_data.json", "w") as f:
        json.dump(attendance_data, f, indent=2)

    return jsonify({"message": "Attendance updated.", "data": attendance_data[date]})


@app.route('/attendance-summary')
def attendance_summary_page():
    attendance_data_path = "data/attendance_data.json"
    subject_stats = {}

    # ✅ Load attendance data from disk freshly
    if os.path.exists(attendance_data_path):
        with open(attendance_data_path) as f:
            attendance_data = json.load(f)
    else:
        attendance_data = {}

    # ✅ Summarize
    for date, records in attendance_data.items():
        for subject, status in records.items():
            if not subject or subject.strip().isdigit():
                continue
            if subject not in subject_stats:
                subject_stats[subject] = {"P": 0, "A": 0}
            if status in ["P", "A"]:
                subject_stats[subject][status] += 1

    summary = []
    for subject, stats in subject_stats.items():
        total = stats["P"] + stats["A"]
        percent = (stats["P"] / total * 100) if total else 0
        summary.append({
            "subject": subject,
            "present": stats["P"],
            "absent": stats["A"],
            "total": total,
            "percentage": round(percent, 1)
        })

    return render_template("attendance_summary.html", summary=summary)



@app.route('/vacation-planner', methods=["GET"])
def vacation_modal_page():
    return render_template("vacation_planner.html")  # <-- Tailwind-based UI page

@app.route("/api/vacation-plan", methods=["POST"])
def vacation_planner():
    from vacation_logic import generate_vacation_plan_response
    from groq_module import get_vacation_plan_from_groq

    if not request.is_json:
        return jsonify({"error": "Invalid content type"}), 400

    data = request.get_json()
    threshold = int(data.get("threshold", 75))
    preferred_month = data.get("month")

    try:
        with open("data/attendance_data.json") as f:
            raw_attendance = json.load(f)

        # ✅ Subject-wise summary
        summary = {}
        for date, records in raw_attendance.items():
            for subject, status in records.items():
                if subject not in summary:
                    summary[subject] = {"present": 0, "absent": 0}
                if status == "P":
                    summary[subject]["present"] += 1
                elif status == "A":
                    summary[subject]["absent"] += 1

        with open("data/extracted_holidays.json") as f:
            holidays_raw = json.load(f)
            holidays = list(holidays_raw.keys()) if isinstance(holidays_raw, dict) else []

        groq_result = get_vacation_plan_from_groq(
            summary,
            holidays,
            "2025-06-01", "2025-11-30",
            threshold,
            preferred_month
        )

        if groq_result and "suggested_range" in groq_result:
            return jsonify(groq_result)

    except Exception as e:
        print("[Fallback to local logic triggered]", e)

    return jsonify(generate_vacation_plan_response(data))


@app.route('/upload-calendar', methods=["POST"])
def handle_calendar_upload():
    file = request.files.get("file")
    if not file:
        return "No file uploaded", 400

    filename = secure_filename(file.filename)
    file_bytes = file.read()

    # OCR PDF
    if filename.lower().endswith(".pdf"):
        try:
            images = convert_from_bytes(file_bytes)
            extracted_text = ""
            for img in images:
                extracted_text += pytesseract.image_to_string(img)
        except:
            return "PDF processing failed", 500
    else:
        # OCR Image
        try:
            image = Image.open(io.BytesIO(file_bytes))
            extracted_text = pytesseract.image_to_string(image)
        except:
            return "Image processing failed", 500

    # 🔍 Use AI/Regex module to extract holidays
    from groq_module import extract_holidays_from_groq
    holiday_dict = extract_holidays_from_groq(extracted_text)

    # 💾 Save to file
    with open("data/extracted_holidays.json", "w") as f:
        json.dump(holiday_dict, f, indent=2)

    return redirect("/holiday-results")

@app.route("/api/chat-query", methods=["POST"])
def chat_query():
    data = request.get_json()
    question = data.get("query", "")

    # Load attendance
    with open("data/attendance_data.json") as f:
        attendance = json.load(f)

    # Load selected subjects
    with open("data/selected_subjects.json") as f:
        sub = json.load(f)
        subjects = sub.get("selected", []) + sub.get("custom", [])

    # Load holidays
    with open("data/extracted_holidays.json") as f:
        holidays = json.load(f)

    sem_start = datetime(2025, 6, 1)
    sem_end = datetime(2025, 11, 30)

    summary = calculate_subject_wise_summary(attendance, subjects, sem_start, sem_end)

    response = ask_groq_chatbot(question, summary, holidays, subjects, sem_start.strftime("%Y-%m-%d"), sem_end.strftime("%Y-%m-%d"))

    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True)
