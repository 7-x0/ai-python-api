from flask import Flask, request, jsonify
from ai import ask
from memory import load, save, get_user
from voice import stt, tts
from utils import split_text

app = Flask(__name__)

@app.route("/")
def home():
    return "Phos Modular 💙"

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json

    text = d.get("text","")
    image = d.get("image")
    file = d.get("file","")
    audio = d.get("audio")
    uid = d.get("user_id")
    name = d.get("username")

    mem = load()
    user = get_user(mem, uid, name)

    # 🎤 صوت → نص
    if audio:
        text = stt(audio)

    # 💬 history
    user["history"].append(text)
    user["history"] = user["history"][-10:]

    # 🧠 mood
    mood = ask([
        {"role":"system","content":"happy, neutral, annoyed"},
        {"role":"user","content":text}
    ])
    user["mood"] = "neutral"
    if "happy" in mood: user["mood"]="happy"
    elif "annoyed" in mood: user["mood"]="annoyed"

    # 🧠 context
    ctx = f"""
Phos AI

Mood: {user["mood"]}
History: {user["history"]}

Talk Arabic naturally
"""

    content = text
    if image:
        content += f"\nImage: {image}"

    # 📄 file
    if file:
        parts = split_text(file)
        out = []
        for p in parts:
            out.append(ask([
                {"role":"system","content":ctx},
                {"role":"user","content":p}
            ]))
        final = "\n".join(out)
    else:
        final = ask([
            {"role":"system","content":ctx},
            {"role":"user","content":content}
        ])

    # 💬 save
    user["history"].append(final)
    mem["users"][uid] = user
    save(mem)

    audio_file = tts(final)

    return jsonify({
        "result": final,
        "audio": audio_file
    })

app.run(host="0.0.0.0", port=3000)