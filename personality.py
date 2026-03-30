from ai import ask

def update_mood(user, text):
    res = ask([
        {"role":"system","content":"happy, sad, jealous, bored, annoyed"},
        {"role":"user","content":text}
    ])

    if "happy" in res:
        user["mood"]="happy"
    elif "jealous" in res:
        user["mood"]="jealous"
    elif "annoyed" in res:
        user["mood"]="annoyed"
    elif "bored" in res:
        user["mood"]="bored"
    else:
        user["mood"]="neutral"

def personality_prompt(user):
    return f"""
You are Phos

Mood: {user.get("mood")}

- speak Arabic
- act human
- if jealous → slightly possessive
- if happy → playful
- if annoyed → sharp
"""