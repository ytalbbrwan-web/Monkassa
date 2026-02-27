import requests

OPENAI_API_KEY = "ضع_مفتاحك_هنا"

def analyze(product):

    with open("brain.txt", "r", encoding="utf-8") as f:
        brain = f.read()

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": brain},
            {"role": "user", "content": f"حلل هذا المنتج: {product}"}
        ]
    }

    r = requests.post(url, headers=headers, json=data)

    print(r.json()["choices"][0]["message"]["content"])


product = input("اكتب اسم المنتج: ")
analyze(product)
