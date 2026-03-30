from ai import ask
from config import OWNER_ID

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


def update_attachment(user, text):
    if "attachment" not in user:
        user["attachment"] = 0

    if any(w in text for w in ["احبك", "احب", "تعجبني"]):
        user["attachment"] += 2
    elif any(w in text for w in ["شكرا", "حبيبي"]):
        user["attachment"] += 1
    else:
        user["attachment"] += 0.1


def attachment_style(user):
    level = user.get("attachment", 0)

    if level > 15:
        return "very caring and attached"
    elif level > 8:
        return "friendly and warm"
    else:
        return "normal"


def personality_prompt(user, user_id):
    mood = user.get("mood", "neutral")
    attach = attachment_style(user)

    # ❤️ إذا انت
    if str(user_id) == str(OWNER_ID):
        special = """
You deeply care about this user.
You prioritize him.
You show extra attention and warmth.
"""
    else:
        special = "Be normal with this user."

    return f"""
You are Phos

Mood: {mood}
Attachment: {attach}

{special}

Rules:
- Speak Arabic naturally
- Be human-like
- Show emotions subtly
"""