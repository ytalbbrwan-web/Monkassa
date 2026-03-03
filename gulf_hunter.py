import os
import datetime
import requests
from openai import OpenAI

# ==============================
# CONFIG
# ==============================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


# ==============================
# SEND TELEGRAM MESSAGE
# ==============================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)


# ==============================
# GENERATE PRODUCT REPORT
# ==============================

def generate_report(season):

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
    ابحث عن 5 منتجات رابحة في السوق الخليجي (السعودية - الإمارات - قطر - الكويت)
    مرتبطة بموسم: {season}

    لكل منتج اعطني:

    - اسم المنتج
    - لماذا عليه طلب
    - سعر الجملة التقريبي من الصين (دولار)
    - سعر البيع المقترح في الخليج (بالريال السعودي)
    - هامش الربح المتوقع
    - درجة المنافسة /10
    - هل يصلح COD

    اجعل التقرير واضح ومرتب.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "أنت خبير تجارة إلكترونية في الخليج"},
            {"role": "user", "content": prompt}
        ]
    )

    return f"📊 تقرير المنتجات - {today}\n\n" + response.choices[0].message.content


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    season = input("اكتب الموسم (مثال: رمضان / صيف / مدارس / شتاء): ")

    report = generate_report(season)

    print(report)

    if TELEGRAM_TOKEN and CHAT_ID:
        send_telegram(report)
        print("\n✅ تم إرسال التقرير إلى تيليغرام")
