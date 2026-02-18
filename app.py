import os
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# ========= ENV =========
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ========= PRODUCT =========
PRODUCT_NAME = "Monkassa"
PRODUCT_PRICE = "3500 دج"
PRODUCT_COLORS = "الأسود و البلوجين"
PRODUCT_SIZES = "36 / 37 / 38 / 39"

# ========= DELIVERY =========
SPECIAL_800 = ["المغير","تقرت","توڨرت"]
SOUTH_1200 = ["ادرار","تمنراست","عين صالح","تيميمون"]
FREE_ORAN = ["وهران","oran"]
ALGIERS = ["الجزائر","الجزائر العاصمة","alger"]
GROUP_800 = ["البيض","النعامة","بشار","غرداية","الوادي","الاغواط","الأغواط","بسكرة"]
EXCLUDED = ["تندوف","اليزي","إليزي"]

def delivery_price(wilaya):
    w = wilaya.strip().lower()

    if w in FREE_ORAN:
        return "🚚 التوصيل مجاني 🎁"

    if w in ALGIERS:
        return "🚚 التوصيل: 500 دج"

    if w in SPECIAL_800:
        return "🏠 للمنزل: 800 دج\n🏢 للمكتب: 50 دج"

    if w in SOUTH_1200:
        return "🏠 للمنزل: 1200 دج\n🏢 للمكتب: 800 دج"

    if w in GROUP_600:
        return "🏠 للمنزل: 600 دج\n🏢 للمكتب: 400 دج"

    if w in EXCLUDED:
        return "⚠️ التوصيل غير متوفر حاليا لهذه الولاية"

    return None

# ========= SEND TELEGRAM =========
def tg_send(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

# ========= AI =========
def ai_reply(user_text):

    if not OPENAI_API_KEY:
        return "مرحبا 👋 كيف نقدر نعاونك؟"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "system",
                "content": "انت بائعة جزائرية في متجر أحذية نسائية اسمه Monkassa. نبيع فقط هذا الحذاء. اقنعي الزبونة بالشراء باختصار."
            },
            {"role": "user", "content": user_text}
        ]
    }

    try:
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=15)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "مرحبا 🌸 تحبي تعرفي السعر ولا التوصيل؟"

# ========= MESSAGE LOGIC =========
def handle_message(text):
    text_lower = text.lower()

    for word in text.split():
        price = delivery_price(word)
        if price:
            return f"🚚 اسعار التوصيل لولاية {word}\n{price}"
    
    if "توصيل" in text_lower or "شحن" in text_lower:
        return "اكتب اسم ولايتك 📍"

    if "سعر" in text_lower or "ثمن" in text_lower:
        return f"💰 سعر {PRODUCT_NAME}: {PRODUCT_PRICE}"

    if "لون" in text_lower or "الوان" in text_lower:
        return f"🎨 الالوان المتوفرة: {PRODUCT_COLORS}"

    if "مقاس" in text_lower or "مقاسات" in text_lower:
        return f"📏 المقاسات: {PRODUCT_SIZES}"

    return ai_reply(text)

# ========= TELEGRAM WEBHOOK =========
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.json
    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text","")
    tg_send(chat_id, handle_message(text))
    return "ok"

# ================= FACEBOOK VERIFY =================
@app.route("/facebook", methods=["GET"])
def facebook_verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == "monkassa_verify":
        return challenge, 200

    return "error", 403

# ================= FACEBOOK RECEIVE =================
@app.route("/facebook", methods=["POST"])
def facebook_webhook():
    data = request.json

    if "entry" not in data:
        return "ok"

    for entry in data["entry"]:
        for msg in entry.get("messaging", []):

            sender = msg["sender"]["id"]

            if "message" in msg and "text" in msg["message"]:
                text = msg["message"]["text"]
                reply = handle_message(text)

                requests.post(
                    f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}",
                    json={
                        "recipient": {"id": sender},
                        "message": {"text": reply}
                    }
                )

    return "ok"

# ========= ROOT =========
@app.route("/")
def home():
    return "Monkassa bot running"
