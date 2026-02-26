from flask import Flask, request
import requests
import os

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

# ====== معلومات المنتج ======
PRODUCT_NAME = "حذاء نسائي طبي"
PRICE = "3500 دج"
SIZES = "36 / 37 / 38 / 39 / 40"
COLORS = "أسود - بيج - أبيض"

# ====== ذكاء اصطناعي بسيط ======
def ai_reply(text):
    return "مرحبا 👋 نحن متجر موضة الأحذية 👠\nاسأليني عن السعر أو المقاسات أو التوصيل ❤️"

# ====== ارسال رسالة ======
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

# ====== Webhook ======
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == "123456":
        return request.args.get("hub.challenge")
    return "error"

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    for entry in data["entry"]:
        for messaging in entry["messaging"]:

            if "message" not in messaging:
                continue

            sender_id = messaging["sender"]["id"]
            user_text = messaging["message"].get("text","").lower()

            # ===== السعر =====
            if "سعر" in user_text or "ثمن" in user_text or "price" in user_text:
                reply = f"💰 سعر {PRODUCT_NAME} هو {PRICE}"

            # ===== المقاسات =====
            elif "مقاس" in user_text:
                reply = f"📏 المقاسات المتوفرة: {SIZES}"

            # ===== الألوان =====
            elif "لون" in user_text:
                reply = f"🎨 الألوان المتوفرة: {COLORS}"

            # ===== ولايات خاصة =====
            elif "بسكرة" in user_text:
                reply = "🚚 التوصيل إلى بسكرة:\n🏠 للمنزل 800 دج\n📦 للمكتب 500 دج"

            elif "تمنراست" in user_text:
                reply = "🚚 التوصيل إلى تمنراست:\n🏠 للمنزل 1200 دج\n📦 للمكتب 800 دج"

            # ===== باقي الولايات =====
            elif "توصيل" in user_text or "شحن" in user_text:
                reply = "🚚 التوصيل لباقي الولايات:\n🏠 للمنزل 600 دج\n📦 للمكتب 400 دج"

            # ===== رد الذكاء =====
            else:
                reply = ai_reply(user_text)

            send_message(sender_id, reply)

    return "ok", 200


@app.route("/")
def home():
    return "Monkassa Facebook Bot Running"
