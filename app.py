import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


@app.route("/")
def home():
    return "Bot is running!"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = handle_message(text)

        requests.post(URL, json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"


def handle_message(text):
    text = text.lower()

    if "مرحبا" in text:
        return "أهلا بك 👋"

    elif "من انت" in text:
        return "أنا بوت Monkassa 🤖"

    elif "منتج" in text:
        return "قريبا سنعرض أحدث الأحذية 🔥"

    else:
        return "لم أفهم سؤالك 🤔"


# مهم جدا ل Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
