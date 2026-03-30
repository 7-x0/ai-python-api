import hashlib, time

CACHE = {}

def cache_key(x):
    return hashlib.md5(str(x).encode()).hexdigest()

def cache_get(k):
    if k in CACHE and time.time() - CACHE[k]["t"] < 60:
        return CACHE[k]["v"]

def cache_set(k, v):
    CACHE[k] = {"v": v, "t": time.time()}

def split_text(text, size=2000):
    return [text[i:i+size] for i in range(0, len(text), size)]