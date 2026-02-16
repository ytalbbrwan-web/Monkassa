import os
import requests
from flask import Flask, request
from openai import OpenAI
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ---------------- وقت العمل ----------------
def is_night():
    h = datetime.now().hour
    return h >= 23 or h < 10

# ---------------- ارسال رسالة ----------------
def send(chat_id,text):
    requests.post(telegram_url,json={"chat_id":chat_id,"text":text})

# ---------------- رابط المكتب ----------------
def office_map_link(text):
    words=text.split()
    for w in words:
        if len(w)>3:
            return f"https://www.google.com/maps/search/ZR+Express+{w}"
    return None

# ---------------- حساب التوصيل ----------------
home_600=["مستغانم","الشلف","البليدة","باتنة","عنابة","سوق اهراس","تموشنت","تلمسان","بلعباس","تيسمسيلت","تيزي وزو","بجاية","البويرة","تبسة","تيارت","جيجل","سطيف","سعيدة","سكيكدة","قالمة","قسنطينة","المدية","بومرداس","خنشلة","ميلة","ام البواقي","عين الدفلى","الطارف","غليزان"]
home_800=["بشار","الاغواط","بسكرة","الجلفة","ورقلة","البيض","الوادي","توقرت"]
home_1200=["ادرار","تمنراست","اولاد جلال","عين صالح","تيميمون","بني عباس","المغير"]

def delivery_price(msg):
    for w in home_600:
        if w in msg:
            return "🚚 التوصيل للدار 600 دج\n🏢 للمكتب 500 دج عبر ZR Express"

    for w in home_800:
        if w in msg:
            return "🚚 التوصيل للدار 800 دج\n🏢 للمكتب 800 دج عبر ZR Express"

    for w in home_1200:
        if w in msg:
            return "🚚 التوصيل للدار 1200 دج\n🏢 للمكتب 800 دج عبر ZR Express"

    if "الجزائر" in msg:
        return "🚚 التوصيل للدار 500 دج\n🏢 للمكتب 500 دج"

    if "وهران" in msg:
        return "🚚 التوصيل مجاني للدار 🎁\n🏢 للمكتب 500 دج"

    return None

# ---------------- AI الرد ----------------
def ai_reply(msg):

    # مكتب
    if "مكتب" in msg:
        link=office_map_link(msg)
        if link:
            return f"تقدري تروحي لأقرب مكتب ZR Express 📍\n{link}"

    # حساب التوصيل
    price=delivery_price(msg)
    if price:
        return price

    # ذكاء اصطناعي
    response=client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"""
أنت بائعة جزائرية في بوتيك MONKASSA.
جاوبي باحتراف وبدون إطالة.

المعلومات:
السعر 3500 دج
مقاسات 36/37/38/39
الألوان الأسود والبلوجين
لاصومال طبية +5سم طول
التوصيل 24 ساعة
القياس عند الاستلام وارجاع مجاني

إذا حبت تطلب:
اطلبي الاسم + الرقم + الولاية + البلدية + المقاس + اللون
"""},

            {"role":"user","content":msg}
        ],
        temperature=0.6
    )

    return response.choices[0].message.content

# ---------------- Webhook ----------------
@app.route("/webhook",methods=["POST"])
def webhook():
    data=request.get_json()

    if "message" not in data:
        return "ok"

    chat_id=data["message"]["chat"]["id"]
    text=data["message"].get("text","")

    if not is_night():
        return "ok"

    reply=ai_reply(text)
    send(chat_id,reply)
    return "ok"

@app.route("/")
def home():
    return "BOT RUNNING"

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
