import requests

API_KEY = "YOUR_KEY"

def generate_image(prompt):
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model":"gpt-image-1","prompt":prompt}
    )
    return r.json()["data"][0]["url"]

def analyze_video(url):
    return f"🎥 هذا فيديو: {url}"