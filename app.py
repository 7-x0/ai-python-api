from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

API_KEY = "حط_مفتاح_OpenAI_هنا"

MEMORY_FILE = "memory.json"

# 🔹 تحميل الذاكرة
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"users": {}, "global": {"notes": []}}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

# 🔹 حفظ الذاكرة
def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)

# 🔹 GPT request
def ask_gpt(messages):
    res = requests.post(
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
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "صار خطأ ❌"

# 🔹 تقسيم النص
def split_text(text, size=2000):
    return [text[i:i+size] for i in range(0, len(text), size)]

@app.route("/")
def home():
    return "Phos شغال 💙"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    text = data.get("text", "")
    image = data.get("image", None)
    file = data.get("file", "")
    user_id = data.get("user_id", "unknown")
    username = data.get("username", "unknown")

    memory = load_memory()

    # 👤 ذاكرة المستخدم
    user_memory = memory["users"].get(user_id, {
        "name": username,
        "notes": []
    })

    # 👥 ذاكرة مشتركة
    global_memory = memory["global"].get("notes", [])

    # 🧠 Intent Detection
    intent_raw = ask_gpt([
        {
            "role": "system",
            "content": """
Classify the request into:
chat, code, image

Return only one word.
"""
        },
        {
            "role": "user",
            "content": f"{text}\nImage: {image}"
        }
    ])

    if "code" in intent_raw.lower():
        intent = "code"
    elif "image" in intent_raw.lower():
        intent = "image"
    else:
        intent = "chat"

    # 🧠 استخراج ذاكرة جديدة
    memory_extract = ask_gpt([
        {
            "role": "system",
            "content": """
Extract important memory.

Return JSON:
{ "save": true/false, "type": "user/global", "data": "..." }
"""
        },
        {
            "role": "user",
            "content": text
        }
    ])

    if "true" in memory_extract.lower():
        if "global" in memory_extract.lower():
            global_memory.append(text)
            memory["global"]["notes"] = global_memory
        else:
            user_memory["notes"].append(text)

    # 💾 حفظ
    memory["users"][user_id] = user_memory
    save_memory(memory)

    # 🧠 تجهيز الذاكرة
    user_context = "\n".join(user_memory["notes"][-5:])
    global_context = "\n".join(global_memory[-5:])

    # 🧠 اختيار النظام
    if intent == "code":
        system_prompt = f"""
You are Phos, a senior software engineer.

User Memory:
{user_context}

Global Memory:
{global_context}

- Fix code
- Find bugs
- Be precise
- Explain in Arabic
"""
    elif intent == "image":
        system_prompt = f"""
You are Phos.

User Memory:
{user_context}

Global Memory:
{global_context}

- Analyze images
- Be smart
- Speak Arabic
"""
    else:
        system_prompt = f"""
You are Phosphophyllite (Phos).

User Memory:
{user_context}

Global Memory:
{global_context}

- Speak Arabic
- Understand English
- Be friendly
- Be smart
"""

    # 🧠 تجهيز المحتوى
    content = text
    if image:
        content += f"\nImage: {image}"

    # 📄 إذا ملف طويل
    if file:
        chunks = split_text(file)
        results = []

        for chunk in chunks:
            res = ask_gpt([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk}
            ])
            results.append(res)

        final = "\n".join(results)
    else:
        final = ask_gpt([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ])

    return jsonify({"result": final})

app.run(host="0.0.0.0", port=3000)