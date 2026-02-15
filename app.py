import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

=====================

ENV VARIABLES

=====================

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN") OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(name)

SYSTEM_PROMPT = """ أنت بائعة حقيقية في بوتيك أحذية نسائية اسمه MONKASSA. تتكلمين مع الزبونة بأسلوب لطيف وقصير مثل بائعة متجر وليس روبوت. لا تذكر أبداً أنك ذكاء اصطناعي.

السعر: 35000 دج المقاسات: 36 / 37 / 38 / 39 الألوان: الأسود - البلوجين نعل طبي + يزيد الطول 5 سم

نبيع أونلاين مع توصيل وهران: مجاني الجزائر العاصمة: 500 دج باقي الولايات حسب المنطقة

يمكن القياس أمام عامل التوصيل وإذا لم يناسب يرجع بدون دفع

عند الطلب اطلبي: رقم الهاتف + الولاية + البلدية + المقاس + اللون

الردود قصيرة وطبيعية مثل بائعة محل """

=====================

TELEGRAM SEND MESSAGE

=====================

def send_message(chat_id, text): url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage" requests.post(url, json={ "chat_id": chat_id, "text": text })

=====================

AI RESPONSE

=====================

def ask_ai(user_message): response = client.chat.completions.create( model="gpt-4.1-mini", messages=[ {"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message} ], temperature=0.7 ) return response.choices[0].message.content

=====================

WEBHOOK

=====================

@app.route("/webhook", methods=["POST"]) def webhook(): data = request.get_json() if "message" in data: chat_id = data["message"]["chat"]["id"] text = data["message"].get("text", "")

ai_reply = ask_ai(text)
    send_message(chat_id, ai_reply)

return jsonify({"ok": True})

@app.route("/", methods=["GET"]) def home(): return "Monkassa bot running"

if name == "main": app.run(host="0.0.0.0", port=10000)
