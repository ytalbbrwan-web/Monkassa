
from flask import Flask, request, jsonify

app = Flask(__name__)

# الصفحة الرئيسية
@app.route("/")
def home():
    return "Monkassa AI is running 🚀"

# هنا الذكاء الاصطناعي
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    message = data.get("message")

    reply = "انت قلت: " + message

    return jsonify({
        "response": reply
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
