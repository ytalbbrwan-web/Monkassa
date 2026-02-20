from flask import Flask, request
import requests
import os

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = "monkassa_verify"

# ================= الرد الذكي =================
def reply_ai(text):
    return f"مرحبا 🌸\nالحذاء متوفر\nتحبي السعر ولا التوصيل؟"

# ================= ارسال رسالة =================
def send_msg(psid, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={
        "recipient": {"id": psid},
        "messaging_type": "RESPONSE",
        "message": {"text": text}
    })

# ================= VERIFY =================
@app.route("/facebook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "error", 403

# ================= RECEIVE =================
@app.route("/facebook", methods=["POST"])
def receive():
    data = request.json

    if data.get("object") == "page":
        for entry in data["entry"]:
            for change in entry["changes"]:
                value = change["value"]

                if "messages" in value:
                    for msg in value["messages"]:
                        if "text" in msg:
                            sender = msg["from"]["id"]
                            text = msg["text"]["body"]

                            answer = reply_ai(text)
                            send_msg(sender, answer)

    return "ok", 200

# ================= ROOT =================
@app.route("/")
def home():
    return "bot running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
