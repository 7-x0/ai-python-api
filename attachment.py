def update_attachment(user, text):
    if "attachment" not in user:
        user["attachment"] = 0

    if "احبك" in text or "احب" in text:
        user["attachment"] += 2
    elif "شكرا" in text:
        user["attachment"] += 1
    else:
        user["attachment"] += 0.2

def attachment_prompt(user):
    level = user.get("attachment", 0)

    if level > 10:
        return "You are emotionally attached, caring and soft"
    elif level > 5:
        return "You are friendly and warm"
    else:
        return "You are normal"