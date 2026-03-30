from ai import ask

def extract_preferences(text):
    return ask([
        {
            "role":"system",
            "content":"extract preferences JSON"
        },
        {
            "role":"user",
            "content":text
        }
    ])