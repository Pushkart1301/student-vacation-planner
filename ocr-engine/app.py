# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for

from flask import Flask, request, jsonify, render_template
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


app = Flask(__name__)
CORS(app)



# Update your static holiday planner
HOLIDAYS = []  # Will be filled by uploaded calendar
USER_THRESHOLD = 75

# @app.route('/vacation-planner', methods=['GET', 'POST'])
# def vacation_planner():
#     global HOLIDAYS, USER_THRESHOLD

#     if request.method == 'POST':
#         threshold = int(request.form.get("threshold", 75))
#         USER_THRESHOLD = threshold

#         file = request.files.get("file")
#         if file:
#             filename = secure_filename(file.filename)
#             file_bytes = file.read()
#             extracted_text = ""

#             if filename.endswith(".pdf"):
#                 with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
#                     for page in pdf.pages:
#                         extracted_text += page.extract_text() or ""
#                 if not extracted_text.strip():
#                     images = convert_from_bytes(file_bytes)
#                     for img in images:
#                         extracted_text += pytesseract.image_to_string(img)
#             else:
#                 img = Image.open(io.BytesIO(file_bytes))
#                 extracted_text = pytesseract.image_to_string(img)

#             from groq_module import extract_holidays_from_groq  # ← Use your actual function
#             HOLIDAYS = extract_holidays_from_groq(extracted_text)

#         return render_template("holiday_results.html", holidays=HOLIDAYS, threshold=USER_THRESHOLD)

#     return render_template("holiday_results.html", holidays=HOLIDAYS, threshold=USER_THRESHOLD)



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

@app.route('/api/lectures-for-date/<date>', methods=['GET'])
def lectures_for_date(date):
    try:
        with open("data/lecture_schedule.json") as f:
            lecture_schedule = json.load(f)

        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
        subjects = lecture_schedule.get(weekday, [])

        return jsonify({"weekday": weekday, "lectures": subjects})
    except Exception as e:
        return jsonify({"error": str(e)})


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
    with open("data/selected_subjects.json", "w") as f:
        json.dump(data, f, indent=2)
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
        lecture_schedule = {}  # fallback if file doesn't exist

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



@app.route("/vacation-planner", methods=["GET", "POST"])
def vacation_planner():
    if request.method == "GET":
        return render_template("vacation_planner.html")

    print("[INFO] /vacation-planner POST called")

    try:
        data = request.get_json()
        print("[INFO] Data received:", data)

        from vacation_logic import generate_vacation_plan_response
        response_data = generate_vacation_plan_response(data)
        print("[INFO] Response data:", response_data)

        return jsonify(response_data)

    except Exception as e:
        print("[ERROR in /vacation-planner POST]:", str(e))
        import traceback
        traceback.print_exc()  # print full error
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
