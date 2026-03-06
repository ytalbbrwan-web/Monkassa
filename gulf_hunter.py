import os
import requests
from flask import Flask, request
from openai import OpenAI

# ====== CONFIG ======
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
FACEBOOK_TOKEN = os.environ.get("FACEBOOK_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# ====== AD ACCOUNTS ======
AD_ACCOUNTS = [
"act_1432813163902616",
"act_791862618472529"
]

# ====== SEND MESSAGE TO TELEGRAM ======
def send_message(chat_id, text):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    requests.post(url, json=payload)

# ====== AI PRODUCT SEARCH ======
def search_products(niche):

    prompt = f"""
    ابحث عن 5 منتجات ترند ومربحة حاليا في الخليج في مجال {niche}.
    اعطني:
    - اسم المنتج
    - سعر الجملة التقريبي بالدولار
    - سعر البيع في الخليج
    - هامش الربح المتوقع
    - لماذا المنتج مطلوب
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "انت خبير تجارة الكترونية في الخليج"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# ====== GET ACTIVE CAMPAIGNS ======
def get_campaigns():

    campaigns_list = []

    for account in AD_ACCOUNTS:

        url = f"https://graph.facebook.com/v19.0/{account}/campaigns"

        params = {
            "fields": "name,status,id",
            "access_token": FACEBOOK_TOKEN
        }

        r = requests.get(url, params=params)

        data = r.json()

        campaigns = data.get("data", [])

        for c in campaigns:

            if c["status"] == "ACTIVE":
                campaigns_list.append(c)

    return campaigns_list


# ====== ANALYZE CAMPAIGN ======
def analyze_campaign(campaign_id):

    url = f"https://graph.facebook.com/v19.0/{campaign_id}/insights"

    params = {
        "fields": "impressions,clicks,ctr,cpc,spend",
        "access_token": FACEBOOK_TOKEN
    }

    r = requests.get(url, params=params)

    data = r.json()

    if "data" not in data or len(data["data"]) == 0:
        return None

    return data["data"][0]


# ====== WEBHOOK ======
@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.get_json()

    if "message" in data:

        chat_id = data["message"]["chat"]["id"]

        text = data["message"].get("text", "")

        if text == "/start":

            send_message(chat_id,"اكتب مجال للبحث عن منتجات\nمثال: أحذية نسائية\n\nاو اكتب: حلل الحملة")

        elif text == "حلل الحملة":

            campaigns = get_campaigns()

            if len(campaigns) == 0:

                send_message(chat_id,"لا توجد حملات نشطة")

            else:

                report = "📊 تحليل الحملات\n\n"

                for c in campaigns:

                    stats = analyze_campaign(c["id"])

                    if not stats:
                        continue

                    ctr = stats.get("ctr","0")
                    cpc = stats.get("cpc","0")
                    spend = stats.get("spend","0")

                    report += f"""
🎯 {c['name']}

CTR : {ctr} %
CPC : {cpc} $
Spend : {spend} $

"""

                send_message(chat_id,report)

        else:

            send_message(chat_id,"🔎 جاري البحث عن منتجات مربحة...")

            result = search_products(text)

            send_message(chat_id,result)

    return "ok"


# ====== ROOT TEST ======
@app.route('/')
def home():
    return "Monkassa AI Running"


# ====== RUN SERVER ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
