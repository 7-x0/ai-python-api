import time

LAST_ACTIVE = {}

def update_activity(user_id):
    LAST_ACTIVE[user_id] = time.time()

def should_ping(user_id):
    if user_id not in LAST_ACTIVE:
        return False

    return time.time() - LAST_ACTIVE[user_id] > 300  # 5 دقايق