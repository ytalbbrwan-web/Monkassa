from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

# ================== CONFIG ==================
VERIFY_TOKEN = "monkassa_verify"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

PRODUCT_NAME = "حذاء Monkassa الطبي"
PRODUCT_PRICE = "4500 دج"
PRODUCT_SIZES = "36 37 38 39"
PRODUCT_COLORS = "أسود - بلوجين"

# ================== AI RESPONSE ==================
def ai_reply(user_text):

    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "انت بائعة جزائرية لطيفة في متجر أحذية نسائية اسم المتجر Monkassa. هدفك اقناع الزبونة بشراء الحذاء بطريقة قصيرة ومباشرة."
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    }

    try:
        r = requests.post("https://api.openai.com/v1/chat/completions",
                          headers=headers, json=data, timeout=20)

        return r.json()["choices"][0]["message"]["content"]

    except:
        return "مرحبا 🌸 تحبي السعر ولا المقاسات؟"

# ================== SEND MESSAGE ==================
def send_message(psid, text):

    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": psid},
        "message": {"text": text}
    }

    requests.post(url, json=payload)

# ================== VERIFY ==================
@app.route("/facebook", methods=["GET"])
def verify():

    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200

    return "error", 403

# ================== RECEIVE MESSAGE ==================
@app.route("/facebook", methods=["POST"])
def receive():

    data = request.get_json()

    if data.get("object") != "page":
        return "ok", 200

    for entry in data["entry"]:
        for messaging_event in entry.get("messaging", []):

            sender_id = messaging_event["sender"]["id"]

            if messaging_event.get("message") and messaging_event["message"].get("text"):
                user_text = messaging_event["message"]["text"]

                reply = ai_reply(user_text)
                send_message(sender_id, reply)

    return "ok", 200

# ================== HOME ==================
@app.route("/")
def home():
    return "Monkassa Facebook Bot Running"

# ================== RUN ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
