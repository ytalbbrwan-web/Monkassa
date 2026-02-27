import os
import requests
from openai import OpenAI
from pytrends.request import TrendReq
import random

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def get_trending_keywords():
    pytrend = TrendReq()
    pytrend.build_payload(
        kw_list=["health", "beauty", "fitness", "home gadget"],
        timeframe="now 7-d"
    )

    related = pytrend.related_queries()
    trends = []

    for key in related:
        if related[key]["top"] is not None:
            for item in related[key]["top"]["query"][:3]:
                trends.append(item)

    return trends[:5]


def analyze_with_ai(trends):

    prompt = f"""
    هذه كلمات ترند حالياً:
    {trends}

    حلل السوق واقترح 5 منتجات مربحة جداً.
    لكل منتج اذكر:
    - سبب الربح
    - سعر الشراء التقريبي
    - سعر البيع
    - هامش الربح
    - درجة المنافسة /10
    - نسبة النجاح /10
    """

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}]
    )

    return res.choices[0].message.content


def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id":CHAT_ID,"text":text}
    )


if __name__ == "__main__":
    trends = get_trending_keywords()
    report = analyze_with_ai(trends)
    send_telegram(report)
