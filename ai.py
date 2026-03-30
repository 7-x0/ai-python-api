import requests
from utils import cache_key, cache_get, cache_set

API_KEY = "حط_مفتاح_OpenAI_هنا"

def ask(messages):
    k = cache_key(messages)
    c = cache_get(k)
    if c: return c

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": "gpt-4.1", "messages": messages}
    )

    try:
        out = r.json()["choices"][0]["message"]["content"]
        cache_set(k, out)
        return out
    except:
        return "خطأ ❌"