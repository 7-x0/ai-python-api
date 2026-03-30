from flask import Flask, request, jsonify
import requests, json, os, hashlib, time

app = Flask(__name__)

API_KEY = "حط_مفتاح_OpenAI_هنا"
MEMORY_FILE = "memory.json"
CACHE = {}

# -------------------- MEMORY --------------------

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {
            "users": {},
            "global": {
                "notes": [],
                "nicknames": {},
                "facts": []
            }
        }
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)

# -------------------- CACHE --------------------

def get_cache_key(text):
    return hashlib.md5(text.encode()).hexdigest()

def cache_get(key):
    if key in CACHE and time.time() - CACHE[key]["time"] < 60:
        return CACHE[key]["value"]
    return None

def cache_set(key, value):
    CACHE[key] = {"value": value, "time": time.time()}

# -------------------- GPT --------------------

def ask_gpt(messages):
    key = get_cache_key(str(messages))
    cached = cache_get(key)
    if cached:
        return cached

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
        out = res.json()["choices"][0]["message"]["content"]
        cache_set(key, out)
        return out
    except:
        return "صار خطأ ❌"

# -------------------- IMAGE GEN --------------------

def generate_image(prompt):
    res = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-image-1",
            "prompt": prompt,
            "size": "1024x1024"
        }
    )
    try:
        return res.json()["data"][0]["url"]
    except:
        return None

# -------------------- SPLIT --------------------

def split_text(text, size=2000):
    return [text[i:i+size] for i in range(0, len(text), size)]

# -------------------- MAIN --------------------

@app.route("/")
def home():
    return "Phos Ultra Memory 💙"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    text = data.get("text", "")
    image = data.get("image")
    file = data.get("file", "")
    video = data.get("video", None)
    user_id = data.get("user_id")
    username = data.get("username")

    memory = load_memory()

    user = memory["users"].get(user_id, {
        "name": username,
        "notes": [],
        "history": [],
        "nicknames": {}
    })

    global_mem = memory["global"]

    # 💬 conversation
    user["history"].append(f"user: {text}")
    user["history"] = user["history"][-10:]

    # 🧠 intent
    intent = ask_gpt([
        {"role": "system", "content": "classify: chat, code, image, generate_image, video"},
        {"role": "user", "content": text}
    ])

    # 🎨 generate image
    if "generate_image" in intent:
        img = generate_image(text)
        return jsonify({"result": f"🖼️ {img}"})

    # 🎥 video
    if video:
        return jsonify({"result": f"🎥 هذا فيديو: {video} (تحليل مبدئي)"})

    # 🧠 extract structured memory
    extract = ask_gpt([
        {
            "role": "system",
            "content": """
Extract structured memory.

Return JSON:
{
 "nickname": "...",
 "fact": "...",
 "global": true/false
}
"""
        },
        {"role": "user", "content": text}
    ])

    try:
        data_mem = json.loads(extract)
        if data_mem.get("nickname"):
            user["nicknames"][username] = data_mem["nickname"]

        if data_mem.get("fact"):
            if data_mem.get("global"):
                global_mem["facts"].append(data_mem["fact"])
            else:
                user["notes"].append(data_mem["fact"])
    except:
        pass

    # 🔎 search memory
    if "شنو قال" in text or "who said" in text:
        all_memory = json.dumps(memory)
        answer = ask_gpt([
            {"role": "system", "content": "search memory and answer"},
            {"role": "user", "content": f"{text}\nMemory:\n{all_memory}"}
        ])
        return jsonify({"result": answer})

    # 🧠 context
    context = f"""
User Memory:
{user["notes"][-5:]}

Global:
{global_mem["facts"][-5:]}

History:
{user["history"]}
"""

    # 🖼️ image
    content = text
    if image:
        content += f"\nImage: {image}"

    # 📄 file
    if file:
        chunks = split_text(file)
        results = []
        for c in chunks:
            results.append(ask_gpt([
                {"role": "system", "content": context},
                {"role": "user", "content": c}
            ]))
        final = "\n".join(results)
    else:
        final = ask_gpt([
            {"role": "system", "content": context},
            {"role": "user", "content": content}
        ])

    user["history"].append(f"phos: {final}")

    memory["users"][user_id] = user
    save_memory(memory)

    return jsonify({"result": final})

app.run(host="0.0.0.0", port=3000)