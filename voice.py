import requests

API_KEY = "حط_مفتاح_OpenAI_هنا"

def stt(url):
    try:
        audio = requests.get(url).content
        r = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={"file": ("voice.ogg", audio), "model": (None, "gpt-4o-mini-transcribe")}
        )
        return r.json().get("text","")
    except:
        return ""

def tts(text):
    r = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model":"gpt-4o-mini-tts","voice":"nova","input":text}
    )
    if r.status_code == 200:
        open("voice.mp3","wb").write(r.content)
        return "voice.mp3"