import requests
import json

GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

def extract_holidays_from_groq(text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Extract holidays from academic calendar. Return only a JSON array of holidays with keys: date, event, and weekday."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        result = response.json()
        print("[DEBUG] Full Groq JSON response:")
        print(json.dumps(result, indent=2))

        message = result["choices"][0]["message"]["content"]
        start = message.find("[")
        end = message.rfind("]") + 1
        if start == -1 or end == -1:
            raise ValueError("No valid JSON array found in Groq response")
        return json.loads(message[start:end])

    except Exception as e:
        print("[Groq ERROR - Holidays]:", e)
        return {"error": str(e)}

def get_vacation_plan_from_groq(attendance_summary, holidays, semester_start, semester_end, threshold, preferred_month):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a smart vacation planner bot.

Based on the student attendance data below, suggest a 3 to 5-day vacation period in month {preferred_month}.
Make sure:
- Each subject’s attendance remains >= {threshold}% after the vacation.
- Prefer holidays/weekends to minimize impact.

Input:
Attendance Summary: {json.dumps(attendance_summary, indent=2)}
Holidays: {json.dumps(holidays, indent=2)}
Semester: {semester_start} to {semester_end}

Output strictly in JSON:
{{
  "suggested_range": ["YYYY-MM-DD", "YYYY-MM-DD"],
  "explanation": "short reason",
  "projected_attendance": {{
    "AUTO": 88.3,
    "IP": 91.2
  }}
}}
"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        result = response.json()
        print("[DEBUG] Groq vacation planner raw response:")
        print(json.dumps(result, indent=2))

        content = result["choices"][0]["message"]["content"].strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        return json.loads(content[start:end])

    except Exception as e:
        print("[Groq ERROR - Vacation Planner]:", e)
        return None

def ask_groq_chatbot(query, attendance_summary, holidays, subjects, sem_start, sem_end):
    prompt = f"""
You are a smart assistant for a student vacation planner.

Subjects: {subjects}
Semester Duration: {sem_start} to {sem_end}
Attendance Summary:
{json.dumps(attendance_summary, indent=2)}
Holidays: {json.dumps(holidays, indent=2)}

Student Question: {query}

Answer clearly and only based on this data.
"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for students."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }

    try:
        response = requests.post(GROQ_URL, headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }, json=payload, timeout=60)

        content = response.json()["choices"][0]["message"]["content"].strip()
        if not content or "I'm sorry" in content or "As an AI" in content:
            return "⚠️ Could not get a proper answer."
        return content

    except Exception as e:
        print("[Groq ERROR - Chatbot]:", e)
        return "❌ AI Assistant failed to respond."
