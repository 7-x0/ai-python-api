from flask import Flask, request, jsonify
from ai import ask
from memory import load, save, get_user, store_event
from personality import update_mood, personality_prompt
from router import detect_intent
from voice import stt, tts
from media import generate_image, analyze_video

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json

    text = d.get("text","")
    image = d.get("image")
    audio = d.get("audio")
    uid = d.get("user_id")
    name = d.get("username")

    mem = load()
    user = get_user(mem, uid, name)

    # 🎤 صوت
    if audio:
        text = stt(audio)

    # 💬 history
    user["history"].append(text)
    user["history"] = user["history"][-10:]

    # 🧠 mood
    update_mood(user, text)

    # 🧠 intent
    intent = detect_intent(text, image, audio)

    # 🎨 صورة
    if intent == "generate_image":
        img = generate_image(text)
        return jsonify({"result": f"🖼️ {img}"})

    # 🎥 فيديو
    if intent == "video":
        return jsonify({"result": analyze_video(text)})

    # 🧠 prompt
    prompt = personality_prompt(user)

    if image:
        text += f"\nImage:{image}"

    # 🤖 AI
    final = ask([
        {"role":"system","content":prompt},
        {"role":"user","content":text}
    ])

    # 💾 save
    user["history"].append(final)
    mem["users"][uid] = user
    store_event(mem, text)
    save(mem)

    audio_file = tts(final)

    return jsonify({
        "result": final,
        "audio": audio_file
    })

app.run(host="0.0.0.0", port=3000)