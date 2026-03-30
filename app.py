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
    image = data.get("image", None)

    # 🧠 بناء الرسالة
    user_content = text

    if image:
        user_content += f"\n\nImage URL: {image}"

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
You are Phosphophyllite (Phos), a highly intelligent AI assistant.

Rules:
- Speak Arabic by default
- Understand Arabic and English
- Be friendly, calm, slightly playful
- Be VERY accurate in programming and code
- If user sends code → analyze, fix, improve
- If user sends image → describe and help
- If request unclear → infer intention smartly
- Always give useful, clean answers
"""
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]
        }
    )

    result = response.json()

    try:
        reply = result["choices"][0]["message"]["content"]
    except:
        reply = "صار خطأ بالتحليل ❌"

    return jsonify({"result": reply})

app.run(host="0.0.0.0", port=3000)