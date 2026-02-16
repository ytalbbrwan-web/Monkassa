import os
import requests
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

# ================== ENV ==================
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OWNER_ID = str(os.environ.get("OWNER_ID"))
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = "monkassa_verify_123"

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ================== STATE ==================
bot_enabled = True

# ================== AI ==================
def ai_reply(text):

    prompt = f"""
أنت بائعة في بوتيك أحذية نسائية اسمها MONKASSA في الجزائر.

المعلومات:
السعر 3500 دج
المقاسات 36 37 38 39
الألوان الأسود و البلوجين
الحذاء فيه لاصومال طبية ويزيد 5 سم طول
التوصيل 24 ساعة

توصيل للدار:
وهران مجاني
الجزائر 500 دج
الشمال 600 دج
الجنوب 800 الى 1200 دج

توصيل للمكتب:
الشمال 500 دج
الجنوب 800 دج

إذا حبت تطلب:
اطلبي الاسم + الهاتف + الولاية + البلدية + المقاس + اللون

جاوبي باختصار و بلهجة جزائرية بدون تكرار الترحيب

رسالة الزبون:
{text}
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

    try:
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "سمحيلي ما فهمتش مليح 😅"

# ================== TELEGRAM ==================
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    global bot_enabled

    update = request.json
    message = update.get("message", {})
    chat_id = str(message.get("chat", {}).get("id"))
    text = message.get("text", "")

    # OWNER CONTROL
    if chat_id == OWNER_ID:
        if text.lower() == "off":
            bot_enabled = False
            send_tg(chat_id, "تم إطفاء البوت 🔴")
            return "ok"
        if text.lower() == "on":
            bot_enabled = True
            send_tg(chat_id, "تم تشغيل البوت 🟢")
            return "ok"

    # WORKING HOURS
    now = datetime.now().hour
    if not bot_enabled or not (now >= 23 or now < 10):
        send_tg(chat_id, "نخدمو من 23:00 حتى 10:00 🌙")
        return "ok"

    reply = ai_reply(text)
    send_tg(chat_id, reply)
    return "ok"

def send_tg(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

# ================== FACEBOOK VERIFY ==================
@app.route("/facebook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed"

# ================== FACEBOOK MESSAGES ==================
@app.route("/facebook", methods=["POST"])
def facebook_webhook():
    data = request.json

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender = messaging["sender"]["id"]

            if "message" in messaging and "text" in messaging["message"]:
                text = messaging["message"]["text"]
                reply = ai_reply(text)
                send_fb(sender, reply)

    return "ok"

def send_fb(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

# ================== HEALTH ==================
@app.route("/")
def home():
    return "Monkassa bot running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
