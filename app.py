import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# ذاكرة لكل زبونة
user_memory = {}

def ask_ai(user_id, user_text):

    # أول مرة تتكلم الزبونة
    if user_id not in user_memory:
        user_memory[user_id] = [
            {
                "role": "system",
                "content": """
أنت بائعة في بوتيك أحذية نسائية اسمها MONKASSA.

تكلمي بدارجة جزائرية طبيعية و قصيرة.
ماتعاوديش الترحيب كل مرة.
كملي الحوار حسب كلام الزبونة فقط.

المعلومات:
السعر: 3500 دج
المقاسات: 36 37 38 39
الألوان: أسود و بلوجين
الحذاء فيه لاصومال طبية + يزيد 5 سم طول
التوصيل 24 ساعة

التوصيل:
وهران: مجاني
الجزائر: 500 دج للدار
معظم الولايات: 600 دج
الجنوب: بين 800 و 1200

إذا أرادت الطلب اطلب:
الاسم
رقم الهاتف
الولاية
اللون
المقاس

إذا سألت التجريب:
تقدر تقيسه قدام الليفرور وإذا ماعجبكش ترجعيه بلا مصاريف

لا تقولي مرحبا في كل رسالة، فقط أول مرة.
"""
            }
        ]

    # نضيف كلام الزبونة
    user_memory[user_id].append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=user_memory[user_id]
    )

    reply = response.choices[0].message.content

    # نحفظ رد البائعة
    user_memory[user_id].append({"role": "assistant", "content": reply})

    return reply


@app.route("/", methods=["GET"])
def home():
    return "Monkassa bot running"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")

        if text:
            reply = ask_ai(chat_id, text)

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply}
            )

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
