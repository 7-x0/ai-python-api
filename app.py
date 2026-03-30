from flask import Flask, request, jsonify
from ai import ask
from memory import load, save, get_user, store_event
from personality import update_mood, update_attachment, personality_prompt
from router import detect_intent
from voice import stt, tts
from media import generate_image, analyze_video
from autonomous import should_speak, generate_topic
from learning import extract_preferences
from awareness import track_event, get_recent_events

app = Flask(__name__)

@app.route("/")
def home():
    return "Phos Ultra Conscious 💙"

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json

    text = d.get("text", "")
    image = d.get("image")
    audio = d.get("audio")
    file = d.get("file", "")
    uid = d.get("user_id")
    name = d.get("username")

    mem = load()
    user = get_user(mem, uid, name)

    # 👁️ تسجيل الحدث
    track_event(mem, f"{name}: {text}")

    # 🎤 صوت → نص
    if audio:
        text = stt(audio)

    # 💬 history
    user["history"].append(text)
    user["history"] = user["history"][-15:]

    # 🧬 تعلم
    try:
        pref = extract_preferences(text)
        if "{" in pref:
            user["notes"].append(pref)
    except:
        pass

    # ❤️ تعلق
    update_attachment(user, text)

    # 🧠 مزاج
    update_mood(user, text)

    # 🧠 Intent
    intent = detect_intent(text, image, audio)

    # 🎨 صورة
    if intent == "generate_image":
        return jsonify({
            "result": generate_image(text),
            "audio": None
        })

    # 🎥 فيديو
    if intent == "video":
        return jsonify({
            "result": analyze_video(text),
            "audio": None
        })

    # 🤖 Autonomous
    if should_speak(user["history"]):
        topic = generate_topic()

        user["history"].append(topic)
        mem["users"][uid] = user
        save(mem)

        return jsonify({
            "result": topic,
            "audio": tts(topic)
        })

    # 👁️ awareness context
    events = get_recent_events(mem)

    system_prompt = f"""
{personality_prompt(user)}

Recent Server Events:
{events}

You are aware of environment
"""

    content = text

    if image:
        content += f"\nImage: {image}"

    # 📄 file (chunking)
    if file:
        parts = [file[i:i+2000] for i in range(0, len(file), 2000)]
        responses = []

        for part in parts:
            responses.append(ask([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": part}
            ]))

        final = "\n".join(responses)
    else:
        final = ask([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ])

    # 💾 حفظ
    user["history"].append(final)
    mem["users"][uid] = user
    store_event(mem, text)
    save(mem)

    # 🎧 صوت
    audio_file = tts(final)

    return jsonify({
        "result": final,
        "audio": audio_file
    })

app.run(host="0.0.0.0", port=3000)