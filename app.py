import os
import requests
from flask import Flask, request

app = Flask(__name__)

# ================== ENV ==================

TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ================== PRODUCT ==================

PRODUCT_PRICE = "3500 دج"
PRODUCT_COLORS = "الأسود و البلوجين"
PRODUCT_SIZES = "36 / 37 / 38 / 39"

# ================== DELIVERY PRICES ==================

HOME_DELIVERY = {
    "east": 60,
    "west": 60,
    "center": 80,
    "south": 120
}

OFFICE_DELIVERY_DEFAULT = 50
OFFICE_DELIVERY_SOUTH = 120
OFFICE_DELIVERY_FREE = ["وهران", "oran"]

# ================== REGIONS ==================

def get_region(wilaya):
    wilaya = wilaya.lower()

    east = ["سطيف","عنابة","قسنطينة","جيجل","سكيكدة","باتنة","تبسة","خنشلة","الطارف","سوق اهراس"]
    west = ["وهران","تلمسان","سيدي بلعباس","معسكر","غليزان","البيض","النعامة","عين تموشنت"]
    center = ["الجزائر","البليدة","تيبازة","بومرداس","المدية","عين الدفلى","الشلف","تيزي وزو","البويرة"]
    south = ["أدرار","تمنراست","إليزي","تندوف","بشار","غرداية","ورقلة","الأغواط","الوادي"]

    if wilaya in east:
        return "east"
    if wilaya in west:
        return "west"
    if wilaya in center:
        return "center"
    if wilaya in south:
        return "south"

    return "center"

def get_delivery_price(wilaya):

    if wilaya.lower() in OFFICE_DELIVERY_FREE:
        office = 0
    elif get_region(wilaya) == "south":
        office = OFFICE_DELIVERY_SOUTH
    else:
        office = OFFICE_DELIVERY_DEFAULT

    region = get_region(wilaya)
    home = HOME_DELIVERY[region]

    return home, office

# ================== TELEGRAM SEND ==================

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage",
                  json={"chat_id": chat_id, "text": text})

# ================== AI ==================

def ai_reply(text):

    if not OPENAI_API_KEY:
        return "مرحبا 👋 كيف نقدر نعاونك؟"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "انت بائعة جزائرية في متجر أحذية نسائية Monkassa تقنعي الزبونة باختصار"},
            {"role": "user", "content": text}
        ]
    }

    r = requests.post("https://api.openai.com/v1/chat/completions",
                      headers=headers, json=data)

    try:
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "مرحبا 🌸 تحبي تعرفي السعر ولا التوصيل؟"

# ================== WEBHOOK ==================

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():

    data = request.json

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")
    text_lower = text.lower()

    # PRODUCT INFO
    if "سعر" in text_lower or "ثمن" in text_lower:
        send_message(chat_id, f"💰 سعر مونكاصا: {PRODUCT_PRICE}")
        return "ok"

    if "لون" in text_lower:
        send_message(chat_id, f"🎨 الألوان المتوفرة: {PRODUCT_COLORS}")
        return "ok"

    if "مقاس" in text_lower:
        send_message(chat_id, f"📏 المقاسات: {PRODUCT_SIZES}")
        return "ok"

    # DELIVERY
    if "توصيل" in text_lower:
        send_message(chat_id, "اكتب اسم ولايتك 📍")
        return "ok"

    # WILAYA PRICE
    home, office = get_delivery_price(text_lower)

    if home:
        send_message(chat_id,
                     f"""🚚 اسعار التوصيل لولاية {text}

🏠 للمنزل: {home} دج
🏢 للمكتب: {office} دج""")
        return "ok"

    # AI fallback
    send_message(chat_id, ai_reply(text))
    return "ok"

# ================== ROOT ==================

@app.route("/")
def home():
    return "Monkassa bot running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
