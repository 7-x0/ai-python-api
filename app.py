from flask import Flask, request, jsonify
import requests, json, os, hashlib, time

app = Flask(__name__)

API_KEY = "حط_مفتاح_OpenAI_هنا"
MEMORY_FILE = "memory.json"

CACHE = {}

# ================= MEMORY =================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {
            "users": {},
            "global": {
                "notes": [],
                "facts": []
            }
        }
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)

# ================= CACHE =================

def cache_key(data):
    return hashlib.md5(str(data).encode()).hexdigest()

def cache_get(key):
    if key in CACHE and time.time() - CACHE[key]["time"] < 60:
        return CACHE[key]["val"]
    return None

def cache_set(key, val):
    CACHE[key] = {"val": val, "time": time.time()}

# ================= GPT =================

def ask_gpt(messages):
    key = cache_key(messages)
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

# ================= STT (Voice → Text) =================

def speech_to_text(audio_url):
    try:
        audio = requests.get(audio_url).content

        res = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={
                "Authorization": f"Bearer {API_KEY}"
            },
            files={
                "file": ("voice.ogg", audio),
                "model": (None, "gpt-4o-mini-transcribe")
            }
        )

        return res.json().get("text", "")
    except:
        return ""

# ================= TTS (Text → Voice) =================

def text_to_speech(text):
    res = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini-tts",
            "voice": "nova",  # 👈 صوت بنت
            "input": text
        }
    )

    if res.status_code == 200:
        filename = "voice.mp3"
        with open(filename, "wb") as f:
            f.write(res.content)
        return filename
    return None

# ================= SPLIT =================

def split_text(text, size=2000):
    return [text[i:i+size] for i in range(0, len(text), size)]

# ================= MAIN =================

@app.route("/")
def home():
    return "Phos Ultra Voice 💙"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    text = data.get("text", "")
    image = data.get("image")
    file = data.get("file", "")
    audio = data.get("audio")  # 👈 صوت
    user_id = data.get("user_id")
    username = data.get("username")

    memory = load_memory()

    user = memory["users"].get(user_id, {
        "name": username,
        "notes": [],
        "history": []
    })

    global_mem = memory["global"]

    # 🎤 إذا صوت → نحوله نص
    if audio:
        text = speech_to_text(audio)

    # 💬 history
    user["history"].append(f"user: {text}")
    user["history"] = user["history"][-10:]

    # 🧠 context
    context = f"""
User Memory: {user["notes"][-5:]}
Global Memory: {global_mem["facts"][-5:]}
History: {user["history"]}
"""

    # 🖼️ صورة
    content = text
    if image:
        content += f"\nImage: {image}"

    # 📄 ملف
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

    # 💬 حفظ
    user["history"].append(f"phos: {final}")
    memory["users"][user_id] = user
    save_memory(memory)

    # 🎧 صوت
    audio_file = text_to_speech(final)

    return jsonify({
        "result": final,
        "audio": audio_file
    })

app.run(host="0.0.0.0", port=3000)