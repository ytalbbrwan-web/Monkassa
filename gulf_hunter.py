import requests
import datetime

# ========= CONFIG =========
OPENAI_KEY = "PUT_OPENAI_KEY"
TELEGRAM_TOKEN = "7973029583:AAHLIdAGHx4pGsb7V4f6us3JdUcs5hncXPM"
CHAT_ID = "1950592877"

# ========= SEND TELEGRAM =========
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

# ========= AI PRODUCT HUNTER =========
def generate_report():

    now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

    prompt = f"""
انت خبير تجارة إلكترونية في الخليج (السعودية، الإمارات، الكويت، قطر، البحرين، عمان).

اعطني 5 منتجات مربحة حالياً في الخليج.

لكل منتج اعطني:
- اسم المنتج
- لماذا مطلوب في الخليج
- سعر شراء تقديري بالدولار
- سعر بيع مناسب بالريال السعودي
- هامش الربح التقريبي
- سكريبت إعلان قصير (15 ثانية)
- اسم براند مقترح

ركز على منتجات سهلة الشحن وقابلة للإعلان في تيك توك.
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=60
    )

    result = r.json()["choices"][0]["message"]["content"]

    final_report = f"🔥 Gulf Product Report\n🕒 {now}\n\n{result}"

    send_telegram(final_report)

# ========= RUN =========
generate_report()
