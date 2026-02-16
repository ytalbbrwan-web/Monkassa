import os
import requests
from flask import Flask, request
from openai import OpenAI
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = 1950592877

client = OpenAI(api_key=OPENAI_API_KEY)
telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ----- الولايات -----

home_600 = ["مستغانم","الشلف","البليدة","باتنة","عنابة","سوق اهراس","تموشنت","تلمسان","بلعباس","تيسمسيلت","تيزي وزو","بجاية","البويرة","تبسة","تيارت","جيجل","سطيف","سعيدة","سكيكدة","قالمة","قسنطينة","المدية","بومرداس","خنشلة","ميلة","ام البواقي","عين الدفلى","الطارف","غليزان"]

home_800 = ["بشار","الاغواط","بسكرة","الجلفة","ورقلة","البيض","الوادي","توقرت"]

home_1200 = ["ادرار","تمنراست","اولاد جلال","عين صالح","تيميمون","بني عباس","المغير"]

south = home_800 + home_1200

def delivery_price(text):

    for w in home_600:
        if w in text:
            return "سعر التوصيل للدار 600 دج 🚚\nوللمكتب 500 دج عبر ZR Express"

    for w in home_800:
        if w in text:
            return "سعر التوصيل للدار 800 دج 🚚\nوللمكتب 800 دج عبر ZR Express"

    for w in home_1200:
        if w in text:
            return "سعر التوصيل للدار 1200 دج 🚚\nوللمكتب 800 دج عبر ZR Express"

    if "الجزائر" in text:
        return "التوصيل للدار 500 دج 🚚\nوللمكتب 500 دج"

    if "وهران" in text:
        return " التوصيل للدار مجاني "

    return None

# ----- وقت العمل -----
def is_night():
    h = datetime.now().hour
    return h >= 23 or h < 10

def send(chat_id,text):
    requests.post(telegram_url,json={"chat_id":chat_id,"text":text})

# ----- AI -----
def ai_reply(msg):

    price = delivery_price(msg)
    if price:
        return price

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role":"system",
                "content":"""
أنت بائعة جزائرية في بوتيك MONKASSA.
تكلمي بدارجة احترافية قصيرة.
ما تعاوديش مرحبا كل مرة.

المعلومات:
السعر 3500 دج
لاصومال طبية +5سم
مقاسات 36/37/38/39
الألوان الأسود والبلوجين
التوصيل 24 ساعة
يمكن القياس عند الاستلام وارجاعه مجانا

إذا حبت تطلب:
اطلبي الاسم + الرقم + الولاية + البلدية + اللون + المقاس
"""
            },
            {"role":"user","content":msg}
        ],
        temperature=0.6
    )
    return response.choices[0].message.content

# ----- Webhook -----
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
    return "working"

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
