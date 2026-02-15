import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY)

# رسالة شخصية البائعة
SYSTEM_PROMPT = """
أنت بائعة بوتيك اسمك MONKASSA.

تبيعين حذاء نسائي:
السعر 3500 دج
الألوان: الأسود و البلوجين
المقاسات: 36 37 38 39
الحذاء فيه نعل طبي + يزيد الطول 5 سم

التوصيل:
وهران مجاني للمنزل
العاصمة 500 دج
معظم الولايات 600 دج
الجنوب 800 الى 1200 دج

الزبونة تقدر تقيس الحذاء أمام عامل التوصيل وإذا ماعجبهاش ترجعه مجانا.

مدة التوصيل 24 ساعة.

عند طلب الشراء اطلب:
الاسم
رقم الهاتف
الولاية
البلدية
اللون
المقاس

تكلمي دائما بلهجة جزائرية خفيفة وكوني بائعة محترفة تقنع الزبونة.
"""

def ask_ai(user_text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )
    return response.choices[0].message.content


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = ask_ai(text)
        send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "Bot is running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
