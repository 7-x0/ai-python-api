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

# 🔹 حفظ
def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)

# 🔹 GPT
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

# 🔹 تقسيم
def split_text(text, size=2000):
    return [text[i:i+size] for i in range(0, len(text), size)]

@app.route("/")
def home():
    return "Phos Memory Ultra 💙"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    text = data.get("text", "")
    image = data.get("image", None)
    file = data.get("file", "")
    user_id = data.get("user_id", "unknown")
    username = data.get("username", "unknown")

    memory = load_memory()

    # 👤 user memory
    user = memory["users"].get(user_id, {
        "name": username,
        "notes": [],
        "history": []
    })

    # 👥 global memory
    global_notes = memory["global"].get("notes", [])

    # 💬 Conversation history
    user["history"].append(f"user: {text}")
    user["history"] = user["history"][-10:]  # آخر 10 رسائل

    # 🧠 Intent
    intent_raw = ask_gpt([
        {"role": "system", "content": "Classify: chat, code, image"},
        {"role": "user", "content": f"{text}\nImage: {image}"}
    ])

    if "code" in intent_raw:
        intent = "code"
    elif "image" in intent_raw:
        intent = "image"
    else:
        intent = "chat"

    # 🧠 استخراج ذاكرة
    mem_extract = ask_gpt([
        {
            "role": "system",
            "content": """
Extract memory.

Return JSON:
{ "save": true/false, "type": "user/global", "data": "..." }
"""
        },
        {"role": "user", "content": text}
    ])

    if "true" in mem_extract.lower():
        if "global" in mem_extract.lower():
            global_notes.append(text)
            memory["global"]["notes"] = global_notes
        else:
            user["notes"].append(text)

    # 🔎 Memory search (سؤال عن شخص)
    if "شنو قال" in text or "who said" in text:
        search_context = "\n".join(global_notes + user["notes"])

        answer = ask_gpt([
            {"role": "system", "content": "Search memory and answer"},
            {"role": "user", "content": f"{text}\nMemory:\n{search_context}"}
        ])

        return jsonify({"result": answer})

    # 🧠 Context
    user_context = "\n".join(user["notes"][-5:])
    global_context = "\n".join(global_notes[-5:])
    history_context = "\n".join(user["history"])

    # 🧠 system prompt
    system_prompt = f"""
You are Phosphophyllite (Phos).

User Memory:
{user_context}

Global Memory:
{global_context}

Conversation:
{history_context}

Rules:
- Speak Arabic
- Understand English
- Be smart
- Use memory
"""

    # 🖼️ صورة
    content = text
    if image:
        content += f"\nImage: {image}"

    # 📄 ملف طويل
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

    # 💬 حفظ الرد بالمحادثة
    user["history"].append(f"phos: {final}")

    memory["users"][user_id] = user
    save_memory(memory)

    return jsonify({"result": final})

app.run(host="0.0.0.0", port=3000)