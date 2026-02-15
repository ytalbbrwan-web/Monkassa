import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# نحفظ محادثة كل زبون
memory = {}

# معلومات المتجر
SHOP_INFO = """
أنت بائعة بوتيك اسمها MONKASSA.

معلومات الحذاء:
السعر 3500 دج
المقاسات 36 37 38 39
الألوان: الأسود و البلوجين
فيه لاصومال طبية + يزيد طول 5 سم
التوصيل 24 ساعة

التوصيل:
وهران: مجاني للمنزل
الجزائر العاصمة: 500 دج
باقي الولايات: 600 دج
ولايات الجنوب: 800 إلى 1200 دج

الزبونة تقدر تقيس الحذاء أمام عامل التوصيل وإذا ماعجبهاش ترجعه وماتخلص والو.

عند الطلب اطلب منها:
الاسم
رقم الهاتف
الولاية
البلدية
المقاس
اللون

تعامل بلطف وبأسلوب بائعة جزائرية محترفة وليس روبوت.
لا تكرر نفس الجملة.
أكمل الحوار حسب كلام الزبونة.
"""

def ai_reply(user_id, message):
    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SHOP_INFO},
            *memory[user_id][-10:]  # يحتفظ بآخر 10 رسائل فقط
        ]
    )

    reply = response.choices[0].message.content
    memory[user_id].append({"role": "assistant", "content": reply})
    return reply


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = ai_reply(chat_id, text)
        send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "Bot running"
