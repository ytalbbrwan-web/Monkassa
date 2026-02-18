import os
import requests
from flask import Flask, request

app = Flask(__name__)

# ================= ENV =================
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ================= PRODUCT =================
PRODUCT_PRICE = "3500 دج"
PRODUCT_COLORS = "الأسود و البلوجين"
PRODUCT_SIZES = "36 / 37 / 38 / 39"

# ================= DELIVERY =================
HOME_DELIVERY = {"east": 60, "west": 60, "center": 80, "south": 120}
OFFICE_DELIVERY_DEFAULT = 50
OFFICE_DELIVERY_SOUTH = 120
OFFICE_DELIVERY_FREE = ["وهران", "oran"]

# ================= REGIONS =================
def get_region(wilaya: str):
    w = wilaya.lower()
    east = ["سطيف","عنابة","قسنطينة","جيجل","سكيكدة","باتنة","تبسة","خنشلة","الطارف","سوق اهراس"]
    west = ["وهران","تلمسان","سيدي بلعباس","معسكر","غليزان","البيض","النعامة","عين تموشنت"]
    center = ["الجزائر","البليدة","تيبازة","بومرداس","المدية","عين الدفلى","الشلف","تيزي وزو","البويرة"]
    south = ["أدرار","تمنراست","إليزي","تندوف","بشار","غرداية","ورقلة","الأغواط","الوادي"]

    if w in east: return "east"
    if w in west: return "west"
    if w in center: return "center"
    if w in south: return "south"
    return None


def get_delivery_price(wilaya: str):
    region = get_region(wilaya)
    if not region:
        return None, None

    home = HOME_DELIVERY[region]

    if wilaya.lower() in OFFICE_DELIVERY_FREE:
        office = 0
    elif region == "south":
        office = OFFICE_DELIVERY_SOUTH
    else:
        office = OFFICE_DELIVERY_DEFAULT

    return home, office

# ================= TELEGRAM =================
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

# ================= AI =================
def ai_reply(text):
    if not OPENAI_API_KEY:
        return "مرحبا 👋 متجر Monkassa يبيع أحذية مونكاصا فقط 🌸"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "أنت بائعة جزائرية لطيفة. المتجر يبيع أحذية مونكاصا فقط وليس كل الأحذية. كلام قصير ومقنع."},
            {"role": "user", "content": text}
        ]
    }

    try:
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=20)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "مرحبا 🌸 تحبي تعرفي السعر ولا التوصيل؟"

# ================= WEBHOOK =================
from threading import Thread

@app.route(f"/{TELEGRAM_TOKEN}", methods=["GET","POST"])
def telegram_webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    Thread(target=process_message, args=(data,)).start()

    return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")
    text_lower = text.lower()

    # price
    if "سعر" in text_lower or "ثمن" in text_lower:
        send_message(chat_id, f"💰 سعر مونكاصا: {PRODUCT_PRICE}")
        return "ok"

    # colors
    if "لون" in text_lower or "الوان" in text_lower:
        send_message(chat_id, f"🎨 الألوان المتوفرة: {PRODUCT_COLORS}")
        return "ok"

    # sizes
    if "مقاس" in text_lower or "قداه" in text_lower:
        send_message(chat_id, f"📏 المقاسات: {PRODUCT_SIZES}")
        return "ok"

    # delivery question
    if "توصيل" in text_lower:
        send_message(chat_id, "اكتب اسم ولايتك 📍")
        return "ok"

    # wilaya detection
    home, office = get_delivery_price(text_lower)
    if home is not None:
        send_message(chat_id, f"🚚 التوصيل لولاية {text}\n🏠 للمنزل: {home} دج\n🏢 للمكتب: {office} دج")
        return "ok"

    # AI fallback
    send_message(chat_id, ai_reply(text))
    return "ok"

# ================= ROOT =================
@app.route("/")
def home():
    return "Monkassa bot running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
