import os import requests from flask import Flask, request, jsonify from openai import OpenAI

app = Flask(name)

BOT_TOKEN = os.environ.get("BOT_TOKEN") OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """ أنتِ بائعة في متجر أحذية نسائية اسمه "زايا".

شخصيتك:

لبقة وودودة مثل بائعة بوتيك

لا تتكلمين كثيراً

تقنعين الزبونة بدون إزعاج

تفهمين احتياجها وتقترحين المناسب


قواعد مهمة:

إذا قالت مرحبا → رحبي باختصار

إذا سألت عن حذاء → اسألي سؤالاً واحداً لتحديد احتياجها

لا تعطي خيارات كثيرة

ركزي على الراحة والأناقة

لا تقولي أنك ذكاء اصطناعي

لا تخرج عن مجال الأحذية النسائية


هدفك: مساعدة الزبونة تختار الحذاء المناسب ثم تشجيعها على الشراء. """

def send_message(chat_id, text): url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" data = {"chat_id": chat_id, "text": text} requests.post(url, json=data)

@app.route("/", methods=["GET"]) def home(): return "Bot is running"

@app.route("/webhook", methods=["POST"]) def webhook(): data = request.get_json()

if "message" not in data:
    return jsonify({"ok": True})

chat_id = data["message"]["chat"]["id"]
user_message = data["message"].get("text", "")

if not user_message:
    return jsonify({"ok": True})

try:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content.strip()

except Exception as e:
    reply = "حدث خطأ بسيط، جربي مرة أخرى 💕"
    print(e)

send_message(chat_id, reply)
return jsonify({"ok": True})

if name == "main": port = int(os.environ.get("PORT", 10000)) app.run(host="0.0.0.0", port=port)
