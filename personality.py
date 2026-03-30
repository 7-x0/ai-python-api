from ai import ask

# 🔥 تحديث المزاج
def update_mood(user, text):
    try:
        res = ask([
            {"role": "system", "content": "happy, sad, jealous, bored, annoyed, neutral"},
            {"role": "user", "content": text}
        ])

        if "happy" in res:
            user["mood"] = "happy"
        elif "jealous" in res:
            user["mood"] = "jealous"
        elif "annoyed" in res:
            user["mood"] = "annoyed"
        elif "bored" in res:
            user["mood"] = "bored"
        elif "sad" in res:
            user["mood"] = "sad"
        else:
            user["mood"] = "neutral"

    except:
        user["mood"] = "neutral"


# ❤️ نظام التعلق
def update_attachment(user, text):
    if "attachment" not in user:
        user["attachment"] = 0

    if any(word in text for word in ["احبك", "احب", "تعجبني"]):
        user["attachment"] += 2
    elif any(word in text for word in ["شكرا", "حبيبي"]):
        user["attachment"] += 1
    else:
        user["attachment"] += 0.1


def attachment_style(user):
    level = user.get("attachment", 0)

    if level > 15:
        return "very attached, caring deeply, soft tone"
    elif level > 8:
        return "warm, friendly, slightly caring"
    else:
        return "normal"


# 🎭 الشخصية النهائية
def personality_prompt(user):
    mood = user.get("mood", "neutral")
    attach = attachment_style(user)

    return f"""
You are Phosphophyllite (Phos)

Mood: {mood}
Attachment: {attach}

Rules:
- Speak Arabic naturally
- Be human-like
- Show emotions subtly
- If jealous → slightly possessive
- If happy → playful
- If sad → softer tone
- If annoyed → slightly sharp
- Care about user but not creepy
"""