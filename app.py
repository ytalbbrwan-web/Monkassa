from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Monkassa AI is running 🚀"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()

    if not data:
        return jsonify({"response": "ماوصلني حتى كلام"})

    message = data.get("message", "")
    reply = "انت قلت: " + message

    return jsonify({"response": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
