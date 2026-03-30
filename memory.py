import json, os

FILE = "memory.json"

def load():
    if not os.path.exists(FILE):
        return {"users": {}, "global": {"facts": []}}
    return json.load(open(FILE))

def save(mem):
    json.dump(mem, open(FILE, "w"), indent=2)

def get_user(mem, uid, name):
    return mem["users"].get(uid, {
        "name": name,
        "notes": [],
        "history": [],
        "mood": "neutral"
    })
