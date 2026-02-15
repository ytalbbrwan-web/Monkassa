from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# الصفحة الرئيسية
@app.route("/")
def home():
    return "Monkassa AI is running 🚀"

# الذكاء الاصطناعي (تجربة)
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()

    if not data:
        return jsonify({"response": "ماوصلتنيش رسالة"})

    message = data.get("message", "")

    reply = "انت قلت: " + message

    return jsonify({"response": reply})


# تشغيل السيرفر بطريقة يفهمها Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
