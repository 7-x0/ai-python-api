from flask import Flask, request, jsonify
from ai import ask
from memory import load, save, get_user, store_event
from personality import update_mood, personality_prompt
from router import detect_intent
from voice import stt, tts
from media import generate_image, analyze_video
from autonomous import should_speak, generate_topic
from learning import extract_preferences

app = Flask(__name__)

@app.route("/")
def home():
    return "Phos Ultra AI 💙"

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json

    text = d.get("text", "")
    image = d.get("image")
    file = d.get("file", "")
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
    user["history"] = user["history"][-15:]

    # 🧬 Learning System
    try:
        pref = extract_preferences(text)
        if "{" in pref:
            user["notes"].append(pref)
    except:
        pass

    # 🧠 Mood
    update_mood(user, text)

    # 🧠 Intent Detection
    intent = detect_intent(text, image, audio)

    # 🎨 Image Generation
    if intent == "generate_image":
        img = generate_image(text)
        return jsonify({
            "result": f"🖼️ {img}",
            "audio": None
        })

    # 🎥 Video Analysis
    if intent == "video":
        return jsonify({
            "result": analyze_video(text),
            "audio": None
        })

    # 🤖 Autonomous AI (يبادر)
    if should_speak(user["history"]):
        topic = generate_topic()
        user["history"].append(topic)
        mem["users"][uid] = user
        save(mem)

        audio_file = tts(topic)

        return jsonify({
            "result": topic,
            "audio": audio_file
        })

    # 🧠 Personality Prompt
    prompt = personality_prompt(user)

    content = text

    if image:
        content += f"\nImage: {image}"

    # 📄 File handling (chunking)
    if file:
        parts = [file[i:i+2000] for i in range(0, len(file), 2000)]
        responses = []

        for part in parts:
            responses.append(ask([
                {"role": "system", "content": prompt},
                {"role": "user", "content": part}
            ]))

        final = "\n".join(responses)
    else:
        final = ask([
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ])

    # 💾 Save Memory
    user["history"].append(final)
    mem["users"][uid] = user
    store_event(mem, text)
    save(mem)

    # 🎧 Voice Output
    audio_file = tts(final)

    return jsonify({
        "result": final,
        "audio": audio_file
    })

app.run(host="0.0.0.0", port=3000)