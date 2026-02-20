import os
import requests
from flask import Flask, request

app = Flask(__name__)

# ========= TOKENS =========
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ========= PRODUCT =========
PRODUCT_NAME = "Monkassa"
PRODUCT_PRICE = "3500 دج"
PRODUCT_COLORS = "الأسود و البلوجين"
PRODUCT_SIZES = "36 / 37 / 38 / 39"

# ========= DELIVERY =========
def delivery_price(text):
    w = text.lower()

    if "وهران" in w:
        return "🚚 التوصيل مجاني"

    if "الجزائر" in w:
        return "🚚 التوصيل 500 دج"

    south = ["ادرار","تمنراست","عين صالح","تيميمون"]
    for s in south:
        if s in w:
            return "🏠 للدار 1200 دج | 🏢 للمكتب 800 دج"

    group800 = ["البيض","النعامة","بشار","غرداية","الوادي","الاغواط","بسكرة","تقرت","توڨرت","المغير"]
    for g in group800:
        if g in w:
            return "🏠 للدار 800 دج | 🏢 للمكتب 50 دج"

    return None

# ========= TELEGRAM SEND =========
def tg_send(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

# ========= AI =========
def ai_reply(user_text):

    if not OPENAI_API_KEY:
        return "مرحبا 👋 تحبي تعرفي السعر ولا التوصيل؟"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content":
             "انت بائعة جزائرية في متجر Monkassa للأحذية النسائية. نبيع فقط هذا الحذاء. اجابات قصيرة وتقنع الزبونة بالشراء."},
            {"role": "user", "content": user_text}
        ]
    }

    try:
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=15)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "مرحبا 🌸 تحبي تعرفي السعر ولا المقاسات؟"

# ========= MESSAGE LOGIC =========
def handle_message(text):
    t = text.lower()

    # سعر
    if "سعر" in t or "ثمن" in t:
        return f"💰 سعر {PRODUCT_NAME}: {PRODUCT_PRICE}"

    # مقاسات
    if "مقاس" in t or any(x in t for x in ["36","37","38","39"]):
        return f"📏 المقاسات: {PRODUCT_SIZES}"

    # ألوان
    if "لون" in t or "الوان" in t:
        return f"🎨 الالوان: {PRODUCT_COLORS}"

    if "بلوجين" in t:
        return "👌 متوفر بلوجين، اكتب اسمك + الولاية + الهاتف للحجز"

    if "اسود" in t or "أسود" in t:
        return "🖤 متوفر أسود، اكتب اسمك + الولاية + الهاتف للحجز"

    # توصيل
    price = delivery_price(text)
    if price:
        return f"🚚 اسعار التوصيل:\n{price}"

    if "توصيل" in t or "شحن" in t:
        return "اكتب اسم ولايتك نحسبلك التوصيل 📍"

    # AI
    return ai_reply(text)

# ================= TELEGRAM =================
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
    if request.args.get("hub.verify_token") == "monkassa_verify":
        return request.args.get("hub.challenge"), 200
    return "error", 403

# ================= FACEBOOK RECEIVE =================
@app.route("/facebook", methods=["POST"])
def facebook_webhook():
    data = request.json

    if data.get("object") != "page":
        return "ok", 200

    for entry in data.get("entry", []):
        for msg in entry.get("messaging", []):
            sender = msg["sender"]["id"]

            if msg.get("message") and msg["message"].get("text"):
                user_text = msg["message"]["text"]
                reply = handle_message(user_text)

                requests.post(
                    "https://graph.facebook.com/v18.0/me/messages",
                    params={"access_token": PAGE_ACCESS_TOKEN},
                    json={"recipient": {"id": sender}, "message": {"text": reply}}
                )

    return "ok", 200

# ========= ROOT =========
@app.route("/")
def home():
    return "Monkassa bot running"
