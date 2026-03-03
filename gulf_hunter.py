import os
import requests
from flask import Flask, request
from openai import OpenAI

# 🔑 Environment Variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

@app.route("/", methods=["GET"])
def home():
    return "AI Bot Running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        # 🧠 AI Response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت خبير في إيجاد منتجات رابحة في الخليج."},
                {"role": "user", "content": user_text}
            ]
        )

        ai_reply = response.choices[0].message.content

        send_message(chat_id, ai_reply)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
