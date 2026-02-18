import os
import requests
import threading
from flask import Flask, request

app = Flask(__name__)

# ================= ENV =================

TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ================= PRODUCT =================

PRODUCT_NAME = "Monkassa"
PRODUCT_PRICE = "3500 دج"
PRODUCT_COLORS = "الأسود و البلوجين"
PRODUCT_SIZES = "36 / 37 / 38 / 39"

# ================= DELIVERY =================

HOME_DELIVERY = {
    "east": 60,
    "west": 60,
    "center": 80,
    "south": 120
}

OFFICE_DEFAULT = 50
OFFICE_SOUTH = 120
OFFICE_FREE = ["وهران", "oran"]

EAST = ["سطيف","عنابة","قسنطينة","جيجل","سكيكدة","باتنة","تبسة","خنشلة","الطارف","سوق اهراس"]
WEST = ["وهران","تلمسان","سيدي بلعباس","معسكر","غليزان","البيض","النعامة","عين تموشنت"]
CENTER = ["الجزائر","البليدة","تيبازة","بومرداس","المدية","عين الدفلى","الشلف","تيزي وزو","البويرة"]
SOUTH = ["أدرار","تمنراست","إليزي","تندوف","بشار","غرداية","ورقلة","الأغواط","الوادي"]

ALL_WILAYAS = EAST + WEST + CENTER + SOUTH

# ================= HELPERS =================

def get_region(wilaya):
    if wilaya in EAST:
        return "east"
    if wilaya in WEST:
        return "west"
    if wilaya in CENTER:
        return "center"
    if wilaya in SOUTH:
        return "south"
    return "center"

def get_delivery_price(wilaya):
    region = get_region(wilaya)

    if wilaya in OFFICE_FREE:
        office = 0
    elif region == "south":
        office = OFFICE_SOUTH
    else:
        office = OFFICE_DEFAULT

    home = HOME_DELIVERY[region]
    return home, office

def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

# ================= AI =================

def ai_reply(text):
    if not OPENAI_API_KEY:
        return "مرحبا 👋 نبيع غير حذاء Monkassa فقط. تحبي تعرفي السعر ولا التوصيل؟"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "أنت بائعة جزائرية تبيع حذاء Monkassa فقط وليس كل أنواع الأحذية. ردود قصيرة ومقنعة."},
            {"role": "user", "content": text}
        ]
    }

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=8
        )
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "مرحبا 🌸 نبيع غير Monkassa. تحبي السعر ولا المقاسات؟"

# ================= TELEGRAM WEBHOOK =================

@app.route(f"/{TELEGRAM_TOKEN}", methods=["GET", "POST"])
def telegram_webhook():

    if request.method == "GET":
        return "ok"

    data = request.json

    threading.Thread(target=process_message, args=(data,)).start()

    return "ok"

def process_message(data):

    if "message" not in data:
        return

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")
    text_lower = text.lower()

    # السعر
    if "سعر" in text_lower:
        send_message(chat_id, f"💰 سعر {PRODUCT_NAME}: {PRODUCT_PRICE}")
        return

    # الألوان
    if "لون" in text_lower:
        send_message(chat_id, f"🎨 الألوان المتوفرة: {PRODUCT_COLORS}")
        return

    # المقاسات
    if "مقاس" in text_lower:
        send_message(chat_id, f"📏 المقاسات: {PRODUCT_SIZES}")
        return

    # التوصيل
    if text_lower in ALL_WILAYAS:
        home, office = get_delivery_price(text_lower)
        send_message(
            chat_id,
            f"🚚 التوصيل لولاية {text}\n\n🏠 للمنزل: {home} دج\n🏢 للمكتب: {office} دج"
        )
        return

    # ======== SMART REPLY FILTER ========

known_words = [
"سعر","ثمن","بكم",
"لون","الوان",
"مقاس","مقاسات","36","37","38","39",
"توصيل","شحن","delivery"
]

if any(word in text_lower for word in known_words):
    send_message(chat_id, "ممكن توضحي أكثر؟ 🌸")
else:
    send_message(chat_id, ai_reply(text))

return "ok"

# ================= ROOT =================

@app.route("/")
def home():
    return "Monkassa bot running"


