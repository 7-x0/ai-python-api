from flask import Flask, request, jsonify
from ai import ask
from memory import load, save, get_user, store_event
from personality import update_mood, update_attachment, update_jealousy, personality_prompt
from router import detect_intent
from voice import stt, tts
from media import generate_image, analyze_video
from autonomous import should_speak, generate_topic
from learning import extract_preferences
from awareness import track_event, get_recent_events
from social import update_relationships, get_relations
from intervention import should_intervene
from presence import update_activity, should_ping
from config import OWNER_ID

app = Flask(__name__)

@app.route("/")
def home():
    return "Phos Ultra AI 👑💙"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    text = data.get("text", "")
    image = data.get("image")
    audio = data.get("audio")
    file = data.get("file", "")
    user_id = data.get("user_id")
    username = data.get("username")
    is_owner = data.get("is_owner", False)

    memory = load()
    user = get_user(memory, user_id, username)

    # 👁️ تسجيل النشاط
    update_activity(user_id)

    # 👁️ تسجيل الحدث
    track_event(memory, f"{username}: {text}")

    # 🎤 صوت → نص
    if audio:
        text = stt(audio)

    # 💬 history
    user["history"].append(text)
    user["history"] = user["history"][-15:]

    # 🧬 Learning
    try:
        pref = extract_preferences(text)
        if "{" in pref:
            user["notes"].append(pref)
    except:
        pass

    # ❤️ Personality updates
    update_attachment(user, text)
    update_jealousy(user, text)
    update_mood(user, text)

    # 👥 العلاقات
    update_relationships(memory, text)

    # 🧠 Intent
    intent = detect_intent(text, image, audio)

    # 🎨 Image generation
    if intent == "generate_image":
        return jsonify({
            "result": generate_image(text),
            "audio": None
        })

    # 🎥 Video
    if intent == "video":
        return jsonify({
            "result": analyze_video(text),
            "audio": None
        })

    # 👑 Owner ping إذا مختفي
    if str(user_id) == str(OWNER_ID) and should_ping(user_id):
        return jsonify({
            "result": "وينك؟ مختفي اليوم 😏",
            "audio": None
        })

    # 👁️ تدخل بالمحادثة
    if should_intervene(text):
        events = get_recent_events(memory)
        relations = get_relations(memory)

        system_prompt = f"""
{personality_prompt(user, user_id)}

Recent Events:
{events}

Relationships:
{relations}

Join naturally
"""

        final = ask([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ])

        user["history"].append(final)
        memory["users"][user_id] = user
        save(memory)

        return jsonify({
            "result": final,
            "audio": tts(final)
        })

    # 🤖 Autonomous chat
    if text == "auto_think" or should_speak(user["history"]):
        topic = generate_topic()

        user["history"].append(topic)
        memory["users"][user_id] = user
        save(memory)

        return jsonify({
            "result": topic,
            "audio": tts(topic)
        })

    # 🧠 Personality context
    system_prompt = personality_prompt(user, user_id)

    if is_owner:
        system_prompt += "\nYou treat this user as very special."

    content = text
    if image:
        content += f"\nImage: {image}"

    # 📄 ملفات طويلة
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
    memory["users"][user_id] = user
    store_event(memory, text)
    save(memory)

    # 🎧 صوت
    audio_file = tts(final)

    return jsonify({
        "result": final,
        "audio": audio_file
    })

app.run(host="0.0.0.0", port=3000)