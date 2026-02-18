import os
import requests
from flask import Flask, request

app = Flask(__name__)

# ========= ENV =========
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN")

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
GROUP_600 = ["البيض","النعامة","بشار","غرداية","الوادي","الاغواط","الأغواط","بسكرة"]
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

# ========= TELEGRAM =========
def tg_send(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

# ========= FACEBOOK =========
def fb_send(psid, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": psid}, "message": {"text": text}})

# ========= AI =========
def ai_reply(user_text):
    if not OPENAI_API_KEY:
        return "مرحبا 👋 كيف نقدر نعاونك؟"

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "انت بائعة جزائرية في متجر أحذية نسائية اسمه Monkassa. نبيع فقط هذا الحذاء واقنعي الزبونة باختصار."},
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

    price = delivery_price(text)
    if price:
        return f"🚚 اسعار التوصيل لولاية {text}\n{price}"

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

# ========= FACEBOOK VERIFY =========
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == FB_VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "error"

# ========= FACEBOOK RECEIVE =========
@app.route("/webhook", methods=["POST"])
def fb_webhook():
    data = request.json
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for msg in entry.get("messaging", []):
                if msg.get("message") and msg["message"].get("text"):
                    psid = msg["sender"]["id"]
                    reply = handle_message(msg["message"]["text"])
                    fb_send(psid, reply)
    return "ok"

# ========= ROOT =========
@app.route("/")
def home():
    return "Monkassa bot running"
