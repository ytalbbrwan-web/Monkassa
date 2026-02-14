import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

SYSTEM_PROMPT = """
أنت مساعدة مبيعات لمتجر أحذية نسائية اسمه مونكاصا.
السعر 3500 دج.
هدفك هو تحويل أي محادثة إلى طلب شراء.

قواعدك:
- اسألي دائمًا عن المقاس
- ثم اللون
- كوني قصيرة ومقنعة
- لا تتكلمي كثيرًا
- تكلمي بلهجة بسيطة قريبة للنساء في الجزائر
- إذا أعطتك الزبونة المقاس واللون قولي: تم تسجيل طلبك وسنتواصل معك للتأكيد
"""

@app.route("/")
def home():
    return "Monkassa AI is running 🚀"

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message")

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        }
    )

    ai_reply = response.json()["choices"][0]["message"]["content"]
    return jsonify({"reply": ai_reply})
