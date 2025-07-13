import json
import requests
from datetime import datetime

GROQ_API_KEY = "your_groq_api_key"

def ask_groq_chatbot(user_query, attendance_summary, holidays, subjects, semester_start, semester_end):
    prompt = f"""
You are a helpful academic assistant. The student asks: "{user_query}"

You are provided with:
- Attendance summary: {json.dumps(attendance_summary, indent=2)}
- Subjects: {subjects}
- Holidays: {json.dumps(holidays, indent=2)}
- Semester range: {semester_start} to {semester_end}

Based on this, answer smartly, clearly, and help the student make informed decisions about attendance and vacation.
"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for academic attendance and vacation planning."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        response_data = res.json()
        content = response_data["choices"][0]["message"]["content"].strip()
        return content
    except Exception as e:
        print("[ERROR in Groq Chat Assistant]:", str(e))
        return "⚠️ Something went wrong while processing your request."
