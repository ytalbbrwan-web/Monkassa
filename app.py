import os
import requests
from flask import Flask, request
from openai import OpenAI
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = 1950592877

client = OpenAI(api_key=OPENAI_API_KEY)

telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# حالة البوت
bot_enabled = True

def is_night_time():
    now = datetime.now().hour
    return now >= 23 or now < 10

def send(chat_id, text):
    requests.post(telegram_url, json={
        "chat_id": chat_id,
        "text": text
    })

def ai_reply(user_text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
أنت بائعة محترفة في بوتيك أحذية MONKASSA في الجزائر.
تتكلمي بدارجة جزائرية لطيفة و مقنعة.
ما تعاوديش الترحيب كل مرة.
جاوبي مباشرة حسب سؤال الزبونة.

المعلومات:
السعر 3500 دج
المقاسات 36 37 38 39
الألوان: الأسود و البلوچين
نبيع أونلاين مع توصيل

وهران: توصيل مجاني للدار
العاصمة: 500 دج للدار
باقي الولايات شمال: 600 دج
باقي الولايات توصيل مكتب: 500 دج
الجنوب دار: 1200 دج
 ولايات الجنوب للمكتب :800 دج
التوصيل 24 ساعة
القياس قدام الدليفري و إذا ماعجبش ترجعه بلا ماتخلص

إذا حبت تطلب: اطلب منها
الاسم
الرقم
الولاية
البلدية
اللون
المقاس
            """},
            {"role": "user", "content": user_text}
        ]
    )
    return response.choices[0].message.content

@app.route("/", methods=["GET"])
def home():
    return "BOT RUNNING"

@app.route("/webhook", methods=["POST"])
def webhook():
    global bot_enabled

    data = request.get_json()

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    user_id = data["message"]["from"]["id"]
    text = data["message"].get("text", "")

    # أوامر المالك
    if user_id == OWNER_ID:
        if text == "/off":
            bot_enabled = False
            send(chat_id, "تم إطفاء الرد الآلي 🔴")
            return "ok"

        if text == "/on":
            bot_enabled = True
            send(chat_id, "تم تشغيل الرد الآلي 🟢")
            return "ok"

    # التوقيت
    if not bot_enabled or not is_night_time():
        return "ok"

    reply = ai_reply(text)
    send(chat_id, reply)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
