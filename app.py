import requests
import time

TOKEN = "7973029583:AAHLIdAGHx4pGsb7V4f6us3JdUcs5hncXPM
"
URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_updates(offset=None):
    r = requests.get(URL + "getUpdates", params={"timeout": 100, "offset": offset})
    return r.json()

def send_message(chat_id, text):
    requests.get(URL + "sendMessage", params={"chat_id": chat_id, "text": text})

def handle(update):
    if "message" not in update:
        return
    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    # رد البوت
    if text == "/start":
        send_message(chat_id, "أهلا 👋 أنا Monkassa AI")
    else:
        send_message(chat_id, "قلت: " + text)

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if updates["ok"]:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                handle(update)
        time.sleep(1)

main()
