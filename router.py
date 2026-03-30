from ai import ask

def detect_intent(text, image=None, audio=None):
    res = ask([
        {
            "role": "system",
            "content": "classify: chat, code, image, generate_image, video"
        },
        {
            "role": "user",
            "content": f"{text}\nimage:{image}\naudio:{audio}"
        }
    ])

    if "code" in res: return "code"
    if "generate_image" in res: return "generate_image"
    if "image" in res: return "image"
    if "video" in res: return "video"

    return "chat"