import os 
import requests 
from flask import Flask, request

app = Flask(name)

# ================== ENV ==================

TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN") OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ================== PRODUCT (MONKASSA ONLY) ==================

PRODUCT_NAME = "Monkassa" PRODUCT_PRICE = "3500 دج" PRODUCT_COLORS = "أسود / بلوجين" PRODUCT_SIZES = "36 / 37 / 38 / 39"

# ================== DELIVERY ==================

HOME_DELIVERY = {"east": 60, "west": 60, "center": 80, "south": 120} OFFICE_DEFAULT = 50 OFFICE_SOUTH = 120 OFFICE_FREE = ["وهران", "oran"]

EAST = ["سطيف","عنابة","قسنطينة","جيجل","سكيكدة","باتنة","تبسة","خنشلة","الطارف","سوق اهراس"] WEST = ["وهران","تلمسان","سيدي بلعباس","معسكر","غليزان","البيض","النعامة","عين تموشنت"] CENTER = ["الجزائر","البليدة","تيبازة","بومرداس","المدية","عين الدفلى","الشلف","تيزي وزو","البويرة"] SOUTH = ["أدرار","تمنراست","إليزي","تندوف","بشار","غرداية","ورقلة","الأغواط","الوادي"] ALL_WILAYAS = EAST + WEST + CENTER + SOUTH

# ================== HELPERS ==================

def region_of(w): w = w.lower() if w in EAST: return "east" if w in WEST: return "west" if w in SOUTH: return "south" return "center"

def delivery_price(wilaya): region = region_of(wilaya) home = HOME_DELIVERY[region] if wilaya.lower() in OFFICE_FREE: office = 0 elif region == "south": office = OFFICE_SOUTH else: office = OFFICE_DEFAULT return home, office

def send(chat_id, text): requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

# ================== AI ==================

def ai_reply(text): if not OPENAI_API_KEY: return "مرحبا 🌸 نبيعو فقط حذاء Monkassa. تحبي تعرفي السعر ولا التوصيل؟" headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"} data = { "model": "gpt-4.1-mini", "messages": [ {"role": "system", "content": "انت بائعة جزائرية تبيع موديل واحد فقط اسمه Monkassa. الرد يكون قصير جدا (سطرين كحد اقصى) ومباشر للبيع."}, {"role": "user", "content": text} ] } r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) try: return r.json()["choices"][0]["message"]["content"] except: return "نبيعو فقط Monkassa 👟 تحبي السعر ولا التوصيل؟"

# ================== WEBHOOK ==================

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"]) def telegram_webhook(): data = request.json if "message" not in data: return "ok"

chat_id = data["message"]["chat"]["id"]
text = data["message"].get("text", "")
t = text.lower()

# PRICE
if "سعر" in t or "ثمن" in t:
    send(chat_id, f"💰 سعر {PRODUCT_NAME}: {PRODUCT_PRICE}")
    return "ok"

# COLORS
if "لون" in t:
    send(chat_id, f"🎨 الألوان: {PRODUCT_COLORS}")
    return "ok"

# SIZES
if "مقاس" in t or any(x in t for x in ["36","37","38","39"]):
    send(chat_id, f"📏 المقاسات المتوفرة: {PRODUCT_SIZES}")
    return "ok"

# DELIVERY ASK
if "توصيل" in t:
    send(chat_id, "اكتب اسم ولايتك 📍")
    return "ok"

# WILAYA PRICE
if t in ALL_WILAYAS:
    home, office = delivery_price(t)
    send(chat_id, f"🚚 توصيل {t}\n🏠 منزل: {home} دج\n🏢 مكتب: {office} دج")
    return "ok"

# AI
send(chat_id, ai_reply(text))
return "ok"

# ================== ROOT ==================

@app.route("/") def home(): return "Monkassa bot running"

if name == "main": port = int(os.environ.get("PORT", 10000)) app.run(host="0.0.0.0", port=port)
