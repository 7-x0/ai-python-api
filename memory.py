import json, os

FILE = "memory.json"

def load():
    if not os.path.exists(FILE):
        return {
            "global_users": {},
            "guilds": {}
        }
    return json.load(open(FILE))


def save(mem):
    json.dump(mem, open(FILE, "w"), indent=2)


def get_guild(mem, guild_id):
    if guild_id not in mem["guilds"]:
        mem["guilds"][guild_id] = {
            "users": {},
            "relations": [],
            "events": []
        }
    return mem["guilds"][guild_id]


def get_user(guild, user_id, username):
    return guild["users"].get(user_id, {
        "name": username,
        "notes": [],
        "history": [],
        "mood": "neutral"
    })


def get_global_user(mem, user_id):
    if user_id not in mem["global_users"]:
        mem["global_users"][user_id] = {
            "notes": [],
            "history": []
        }
    return mem["global_users"][user_id]