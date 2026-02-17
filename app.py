import os
import requests
from flask import Flask, request

app = Flask(__name__)

# ================= ENV =================
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ================= PRODUCT =================
PRICE = "3500 دج"
COLORS = "الأسود و البلوجين"
SIZES = "36 / 37 / 38 / 39"

# ================= DELIVERY =================
HOME = {"east":60,"west":60,"center":80,"south":120}
OFFICE_DEFAULT = 50
OFFICE_SOUTH = 120
FREE_OFFICE = ["وهران","oran"]

east = ["سطيف","عنابة","قسنطينة","جيجل","سكيكدة","باتنة","تبسة","خنشلة","الطارف","سوق اهراس"]
west = ["وهران","تلمسان","سيدي بلعباس","معسكر","غليزان","البيض","النعامة","عين تموشنت"]
center = ["الجزائر","البليدة","تيبازة","بومرداس","المدية","عين الدفلى","الشلف","تيزي وزو","البويرة"]
south = ["أدرار","تمنراست","إليزي","تندوف","بشار","غرداية","ورقلة","الأغواط","الوادي"]

# ================= HELPERS =================
def region(w):
    w=w.lower()
    if w in east: return "east"
    if w in west: return "west"
    if w in center: return "center"
    if w in south: return "south"
    return None

def delivery(w):
    r=region(w)
    if not r: return None,None
    home=HOME[r]
    if w.lower() in FREE_OFFICE: office=0
    elif r=="south": office=OFFICE_SOUTH
    else: office=OFFICE_DEFAULT
    return home,office

def send(chat,text):
    requests.post(f"{TELEGRAM_API}/sendMessage",json={"chat_id":chat,"text":text})

# ================= AI =================
def ai(text):
    if not OPENAI_API_KEY:
        return "مرحبا 🌸 قوليلي واش تحبي تعرفي؟ السعر ولا التوصيل"

    r=requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization":f"Bearer {OPENAI_API_KEY}"},
        json={
            "model":"gpt-4.1-mini",
            "messages":[
                {"role":"system","content":"انت بائعة جزائرية في متجر أحذية نسائية Monkassa تقنع الزبونة باختصار"},
                {"role":"user","content":text}
            ]
        }
    )
    try:
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "مرحبا 🌸 تحبي السعر ولا التوصيل؟"

# ================= WEBHOOK =================
@app.route(f"/{TELEGRAM_TOKEN}",methods=["POST"])
def hook():
    data=request.json
    if "message" not in data: return "ok"

    chat=data["message"]["chat"]["id"]
    text=data["message"].get("text","")
    t=text.lower()

    if "سعر" in t or "ثمن" in t:
        send(chat,f"💰 سعر مونكاصا: {PRICE}")
        return "ok"

    if "لون" in t:
        send(chat,f"🎨 الألوان: {COLORS}")
        return "ok"

    if "مقاس" in t:
        send(chat,f"📏 المقاسات: {SIZES}")
        return "ok"

    h,o=delivery(t)
    if h:
        send(chat,f"🚚 التوصيل لولاية {text}\n🏠 للمنزل: {h} دج\n🏢 للمكتب: {o} دج")
        return "ok"

    send(chat,ai(text))
    return "ok"

# ================= ROOT =================
@app.route("/")
def home():
    return "Monkassa running"

if __name__ == "__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
