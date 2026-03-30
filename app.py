from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "حط_مفتاح_OpenAI_هنا"

# 🔹 تقسيم النصوص الطويلة
def split_text(text, size=2000):
    return [text[i:i+size] for i in range(0, len(text), size)]

# 🔹 طلب لـ OpenAI
def ask_gpt(messages):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4.1",
            "messages": messages
        }
    )

    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "صار خطأ ❌"

# 🏠 الصفحة الرئيسية
@app.route("/")
def home():
    return "Phos شغال 💙"

# 🧠 التحليل الرئيسي
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    text = data.get("text", "")
    image = data.get("image", None)
    file = data.get("file", "")

    # 🧠 1️⃣ Intent Detection
    intent_prompt = [
        {
            "role": "system",
            "content": """
Classify the request into one of:
chat, code, image_analysis

Return ONLY JSON like:
{ "type": "chat" }
"""
        },
        {
            "role": "user",
            "content": f"{text}\nImage: {image}\nFile: {file[:500]}"
        }
    ]

    intent_raw = ask_gpt(intent_prompt)

    if "code" in intent_raw:
        intent = "code"
    elif "image" in intent_raw:
        intent = "image"
    else:
        intent = "chat"

    # 🧠 2️⃣ اختيار الشخصية
    if intent == "code":
        system_prompt = """
You are a senior software engineer.

- Find ALL bugs
- Fix code
- Improve performance
- Return clean code
- Explain briefly in Arabic
"""
    elif intent == "image":
        system_prompt = """
You are Phosphophyllite (Phos).

- Analyze images deeply
- Describe clearly
- Help user based on image
- Speak Arabic
"""
    else:
        system_prompt = """
You are Phosphophyllite (Phos).

- Speak Arabic by default
- Understand Arabic and English
- Be friendly and smart
- Help clearly and accurately
"""

    # 🧠 3️⃣ تجهيز المحتوى
    user_content = text

    if image:
        user_content += f"\n\nImage URL: {image}"

    # 🧠 4️⃣ إذا أكو ملف طويل → تقسيم
    if file:
        chunks = split_text(file)

        results = []

        for chunk in chunks:
            res = ask_gpt([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk}
            ])
            results.append(res)

        final_result = "\n".join(results)

    else:
        final_result = ask_gpt([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ])

    return jsonify({
        "result": final_result
    })

# 🚀 تشغيل السيرفر
app.run(host="0.0.0.0", port=3000)