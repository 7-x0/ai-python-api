from flask import Flask, request, jsonify
from ai import ask
from memory import load, save, get_user, get_guild, get_global_user
from personality import update_mood, update_attachment, update_jealousy, personality_prompt
from router import detect_intent
from voice import stt, tts
from media import generate_image, analyze_video
from autonomous import should_speak, generate_topic
from learning import extract_memory
from awareness import track_event, get_recent_events
from social import update_relationships, get_relations
from intervention import should_intervene
from presence import update_activity, should_ping
from config import OWNER_ID

app = Flask(__name__)

@app.route("/")
def home():
    return "Phos Ultra AI 💙"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    text = data.get("text", "")
    image = data.get("image")
    audio = data.get("audio")
    file = data.get("file", "")
    user_id = data.get("user_id")
    username = data.get("username")
    guild_id = data.get("guild_id", "default")
    is_owner = data.get("is_owner", False)

    memory = load()

    # 🧠 guild memory
    guild = get_guild(memory, guild_id)
    user = get_user(guild, user_id, username)

    # 👑 global memory (إلك)
    global_user = get_global_user(memory, user_id)

    # 👁️ activity
    update_activity(user_id)

    # 👁️ events
    track_event(guild, f"{username}: {text}")

    # 🎤 صوت → نص
    if audio:
        text = stt(audio)

    # 💬 history
    user["history"].append(text)
    user["history"] = user["history"][-15:]

    # 🧠 AI memory (smart)
    try:
        mem_item = extract_memory(text)

        if mem_item:
            if mem_item["type"] in ["fact", "interest"]:
                user["notes"].append(mem_item["content"])

            elif mem_item["type"] == "relation":
                guild.setdefault("relations", []).append(mem_item["content"])

            # 👑 يخزن الك important إلك بكل مكان
            if is_owner:
                global_user["notes"].append(mem_item["content"])

    except:
        pass

    # ❤️ الشخصية
    update_attachment(user, text)
    update_jealousy(user, text)
    update_mood(user, text)

    # 👥 علاقات
    update_relationships(guild, text)

    # 🧠 intent
    intent = detect_intent(text, image, audio)

    # 🎨 صورة
    if intent == "generate_image":
        return jsonify({"result": generate_image(text), "audio": None})

    # 🎥 فيديو
    if intent == "video":
        return jsonify({"result": analyze_video(text), "audio": None})

    # 👑 نداء إذا اختفيت
    if str(user_id) == str(OWNER_ID) and should_ping(user_id):
        return jsonify({
            "result": "وينك؟ مختفي اليوم 😏",
            "audio": None
        })

    # 👁️ تدخل
    if should_intervene(text):
        events = get_recent_events(guild)
        relations = get_relations(guild)

        system_prompt = f"""
{personality_prompt(user, user_id)}

Recent Events:
{events}

Relationships:
{relations}

Act natural
"""

        final = ask([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ])

        user["history"].append(final)
        guild["users"][user_id] = user
        memory["guilds"][guild_id] = guild
        save(memory)

        return jsonify({
            "result": final,
            "audio": tts(final)
        })

    # 🤖 auto chat
    if text == "auto_think" or should_speak(user["history"]):
        topic = generate_topic()

        user["history"].append(topic)
        guild["users"][user_id] = user
        memory["guilds"][guild_id] = guild
        save(memory)

        return jsonify({
            "result": topic,
            "audio": tts(topic)
        })

    # 🧠 prompt
    system_prompt = personality_prompt(user, user_id)

    if is_owner:
        system_prompt += "\nYou treat this user as very special."

    content = text
    if image:
        content += f"\nImage: {image}"

    # 📄 file
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

    # 💾 save
    user["history"].append(final)
    guild["users"][user_id] = user
    memory["guilds"][guild_id] = guild
    save(memory)

    # 🎧 صوت
    audio_file = tts(final)

    return jsonify({
        "result": final,
        "audio": audio_file
    })

app.run(host="0.0.0.0", port=3000)