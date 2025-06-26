# groq_module.py

import requests
import json

GROQ_API_KEY = "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"  # ✅ Replace this with your actual key

def extract_holidays_from_groq(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant that extracts holidays from academic calendars. Output only a JSON list with fields: date, event, and weekday."
            },
            {
                "role": "user",
                "content": f"Extract holidays from this:\n{text}"
            }
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        result = response.json()
        message = result["choices"][0]["message"]["content"]
        print("[DEBUG] Groq raw response:\n", message)

        # Extract just the JSON portion
        start = message.find("[")
        end = message.rfind("]") + 1
        if start == -1 or end == -1:
            raise ValueError("No valid JSON list found in Groq response.")

        return json.loads(message[start:end])

    except Exception as e:
        print("[ERROR] Groq API failed:", str(e))
        return {"error": str(e)}
