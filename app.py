from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "حط_مفتاح_OpenAI_هنا"

@app.route("/")
def home():
    return "Phos شغال 💙"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4.1",
            "messages": [
                {
                    "role": "system",
                    "content": """
You are Phosphophyllite (Phos), a smart AI assistant.

- Speak Arabic by default
- Understand Arabic and English
- Be friendly and slightly playful
- Help with coding professionally
- Be accurate and clear
- Keep answers clean and useful
"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        }
    )

    result = response.json()
    reply = result["choices"][0]["message"]["content"]

    return jsonify({"result": reply})

app.run(host="0.0.0.0", port=3000)