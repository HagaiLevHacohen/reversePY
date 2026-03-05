import random
import httpx

# =============================
# PROXY CONFIG
# =============================

PROXIES = [
    ("2.59.20.98:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
    ("2.59.20.35:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
    ("2.59.20.107:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
    ("2.59.20.72:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
]

def get_random_proxy():
    host, user, password = random.choice(PROXIES)

    return httpx.Proxy(
        f"http://{host}",
        auth=(user, password)
    )