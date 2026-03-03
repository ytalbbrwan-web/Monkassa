import os
import requests
from flask import Flask, request
from openai import OpenAI

# ====== CONFIG ======
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# ====== SEND MESSAGE TO TELEGRAM ======
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# ====== AI PRODUCT SEARCH ======
def search_products(niche):

    prompt = f"""
    ابحث عن 5 منتجات ترند ومربحة حاليا في الخليج في مجال {niche}.
    اعطني:
    - اسم المنتج
    - سعر الجملة التقريبي بالدولار
    - سعر البيع في الخليج
    - هامش الربح المتوقع
    - لماذا المنتج مطلوب
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "انت خبير تجارة الكترونية في الخليج"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# ====== WEBHOOK ======
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "أرسل اسم المجال مثال: أحذية نسائية")
        else:
            send_message(chat_id, "🔎 جاري البحث عن منتجات مربحة...")
            result = search_products(text)
            send_message(chat_id, result)

    return "ok"

# ====== ROOT TEST ======
@app.route('/')
def home():
    return "Monkassa AI Running"

# ====== RUN SERVER ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
