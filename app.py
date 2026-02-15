from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
API = f"https://api.telegram.org/bot{TOKEN}"

# الصفحة الرئيسية
@app.route("/")
def home():
    return "Monkassa AI running"

# هنا يستقبل تيليغرام الرسائل
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = f"استلمت: {text}"

        requests.post(f"{API}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
