import base64
import json
import math
from datetime import datetime, timezone
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import httpx
import asyncio

# =============================
# CONFIG
# =============================

defaultKey = "kPGxw%f1QAXXJ1AW"

keyPool = [
    "hBz5$zGONcv2Y#zQKDu!OBO8xDql9ymY",
    "lhPEeF66BpECs5AF3D9hYun~PYF~u%91",
    "B2dAQZeD612kt@oyhDtwKlMh#~wccD^x",
    "sbZ#0nmekJpMf3cctZsmG2cS6y^Wp^H7",
    "ETSBKsvCGP6gSkUysyMC#Ugl$QLy4jb%",
    "50xWw~Q#FAib8YUJ3CoiTPu0!Ir8huJx",
    "mEuKN9D44Ntwt$@3fq#uYy$gk!P~4JUb",
    "$!6tSeAy5@TijtJJjqJnh#1iyZwm8Vd1",
    "7O$L5RNImV^Ujt3W~#9k7nJ1uD@doj8j",
    "9Ap0%CHqHa48WdS%AF1m5Fe6qNpKB~hv",
    "gkSq^a2V2de357eFe~Sz2silx7b0gnUL",
    "#^l8@@gBp9F#g@3Qa@x9Ez2gxUQ29q2p",
    "BGmmbrQvI#ms^INWsAb5ryNlXTsPD4Dx",
    "PU9AkFNljqlGg@3Fh%qkIXfRsTI$bERv",
    "p22Cjxw7fgw%NW0CqICWATk9lV54UiSZ",
    "Yk60Roax!PlWbDy4~WsAe@Ju4O2WpFYJ",
    "XiFanqPdaQgrSlnfLg0^u9xgCJi467aE",
    "1wMa2NSLhvYyZ1amsxideohInUMxysJ!",
    "NO$azGmDfH5qVBvUOm130ywm@FPdmIdd",
    "i^eqg!BbQI~tyruwtop#Qj39CRJYPAid",
    "Cu4U0VpDYi$3L!7r~^URVY4RPcgdhu7d",
    "C2jQO#ocTUUaOxObQb$rOAcSSvs@ftRC",
    "l$j3fMuBbqvfSlPu4kHR99Z7hP4Tt%5L",
    "d%uKmqmVgd8Ye%ed@dQUOOmMMIJqSEMV",
    "uiQRWOOV~BpnUh8zuP^se$sAfnb6jRrU",
    "mul1Bnl%od2yTIDM~vWzWBNVy%P4Ym^B",
    "jAVTYgcJWM@#pg@k#HugqZVA120hy0%0",
    "sG9O9TjP4o~kPQ4Os50WKMU^62%EZpaw",
    "D9ig1gPSV6#i$N8m#iHVXCJ~tiemWNRh",
    "!Upvvyc#V$2!M0B0QykbaxcokwqBlCKQ",
    "jcQ$aQiEmzishyQMfwIrvzywBCHR~Q2t",
    "lF!gmgR8jOQQX6fN4^LeIyROM^JHDNB$",
    "^h$bQbY^Bm5@akIxiAG#bzP#s2osl!K^",
    "TVjN%oG%ud1Ru3f8djGI%JOJmslAeKlq",
    "wiXiBXxMynxGAV3!Eb7Dw0y0AU!pLNr!",
    "#G6GfI^0@%Gvyt#f%Xd^R!jL7gHLe%CN",
    "@OvX#UgV6h@%lqvZjXE1LCgns3vbgtKR",
    "@NwoAzRnwp3AUilWk0F3#PsrgB5GjPbb",
    "w4WLf9eIJjF$~XbgAXYXzaeg@pu2EpNa",
    "jcAtnxMm%G9HvYS1zgCm$tpFjp%%Yww4",
    "gq9cZy$rI5wd1HVPgTSA!elhMih5^WH2",
    "bNRwHzkaSeg!Uf7qCQ@1spUzqp0G^qez",
    "Xn30KQ60SCt5K5JP2zaWm35Gin^TfEze",
    "h6q0uFDUEW3g~Ze0PjSdttS8jb62QJ@T",
    "wbOfRsuS@nKqI99#GCZ2SV@YENO#REOw",
    "ESHAUcY42cKNyqox%nTSF9O1QIDWbgJY",
    "@ug0$c85G^m5g!ieG^#GA7QreFjAaadP",
    "~%jYa5uyd~%0@UuBol9VjL@2RMt!S0pT",
    "FvA2Eqhr6yG9qAw!~O6IPNUZNQ#09jfX",
    "3tvPsjHa2c55K4qaGG%%4WxI##99DVnP",
    "r98sxIxXfHy4L#MkaP4WxmOcLncARslB",
    "jwcPYBnQAQt^xUa%OdVY!UEWu8DL@Lyu",
    "pwfIY0c99RZqaiN81PbUGICNPCJ$Hns3",
    "IF2W!g8fQjqbUgZwVJ$Gv@Lpkbf8Bnj~",
    "lmewQMKSmy~tysz~dX@!s7Qs0v9UVgnf",
    "IeNaTNTQCLC@u2CR5!7eGWA5tprqy0wj",
    "YS#Hwx1c1TSyvW8$G7dbpBDi$jfPSXR^",
    "W3rYzkuBmG5Pu3Y@ycgfVNqTNgRpTSdz",
    "pkUcUCgg3OJuvXoMLf@P~!M6H%w$Ad8R",
    "YP1OuEDHhc1pnmya8MZ1JDJ2ynXFBm8@"
]

ivPool = [ 
    "xDZMS#z#7!YKU@B3",
    "nnQ~W%eCLmpDa#z3",
    "gm3kZramMo8ZD%rD",
    "jg6r%R28J8zqIkqP",
    "AZUFfmy3X05ENu8P",
    "W6tm0odAIMSL@Tl$",
    "N^cSZYx%6MyIRpOe",
    "lER0uD2z0v#$S5af",
    "wDgv9N0KPAYfQcLI",
    "Pbg1#5ZNhNN29dBK",
    "g1Lram#jDBoJ9d!V",
    "aRUh!GuiTr%4XH%U",
    "x2kzGSyIY0gbVkN5",
    "zpzDT$b9S3q5^My8",
    "xTlPt@xhV~0aopkA",
    "Y$4^LeCsJiX6weaA",
    "B^rn1blwwSzdyBRA",
    "Oa@FqvHZYou^0%TO",
    "fok^7y0FWONT9fTL",
    "3et3p7ZExVovErfk",
    "DmFkC0Gr5t7t!Bsk",
    "rkactGM3IhM2AwU#",
    "YA0Nu9LKr2T^n#i~",
    "vBARVWaj#mLPrZsB",
    "bv@TEjfnaKiR3KYc",
    "HpBUypo3JhzwH!qf",
    "6bctrthtOfj7zPtj",
    "YnQrmQfu$FwG8U3k",
    "5G$xGLfDhhmWl7w@",
    "%U^7j@!eY0g#%7wr",
    "%N3iLTWYeaMU6znO",
    "!VkwuUJJ#$aq!EC5",
    "QHInRrQ9@ONCBAaj",
    "rFMMvlugQxQv!C^K",
    "~r0fzQtCR0s3AtY^",
    "oTJ$5wb^OfLXKGuL",
    "S!DOOkyO2m#oZhbP",
    "ECpju1WJwnhd9feL",
    "Sk@qmnWZKDS7tymF",
    "tsSyZT2Dz6JaCRZ3",
    "~Ez01YNTTrNC%9#Y",
    "FvSmShNkjm%leZNa",
    "mFWN~hBoOYxLYZk0",
    "pmvfVtWFjQt8ombo",
    "4R4vgrl4TX0dEqAt",
    "ufxtm!H4qFxb!Eag",
    "c~VBDhY5GWkhwcWO",
    "#rRrwPdMO8n6PRO%",
    "#jJxlA96LndGS7EI",
    "5bFy2KHf9GMKS6w~",
    "fjQ^JKusVigE~yjQ",
    "kIsq!^E@TdN^Au^f",
    "tKIo60ypoxKfErLR",
    "2Qf#X~JLujsANvno",
    "%U~r1oTIWx0kPQr8",
    "w!VWba#4S2jA3JKE",
    "p^S$Sjf7WkAjF491",
    "Ytv3qiWLvzwk^MCK",
    "HGs6fodN!Kjf1nAD",
    "cLzNu$S$ckx3mP#R"
]
# =============================
# PRNG (Exact JS Logic)
# =============================

class PRNG:
    def __init__(self, multiplier, increment, modulus, seed):
        self.multiplier = multiplier
        self.increment = increment
        self.modulus = modulus
        self.state = seed

    def Next(self):
        self.state = (self.multiplier * self.state + self.increment) & 0x7fffffff
        return self.state

    def Send(self, seed):
        self.state = seed


prng = PRNG(214013, 2531011, None, 0)


# =============================
# DAILY STATIC KEY
# =============================

def generateDailyStaticKeyAndIV():
    now = datetime.now(timezone.utc)
    start_of_year = datetime(now.year, 1, 1, tzinfo=timezone.utc)
    day_of_year = (now - start_of_year).days + 1

    prng.Send(day_of_year)
    randomValue = prng.Next()

    keyString = keyPool[randomValue % len(keyPool)]
    ivString = ivPool[randomValue % len(ivPool)]

    return keyString.encode("utf-8"), ivString.encode("utf-8")


# =============================
# AES HELPERS
# =============================

def aes_encrypt(data_bytes, key_bytes, iv_bytes):
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    return cipher.encrypt(pad(data_bytes, AES.block_size))


def aes_decrypt(cipher_bytes, key_bytes, iv_bytes):
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    return unpad(cipher.decrypt(cipher_bytes), AES.block_size)


# =============================
# LAYER 1 (Daily Static)
# =============================

def encryptWithDailyStaticKey(data_str):
    staticKey, staticIV = generateDailyStaticKeyAndIV()
    encrypted = aes_encrypt(data_str.encode("utf-8"), staticKey, staticIV)
    return encrypted.hex()


def decryptWithDailyStaticKey(hex_data):
    staticKey, staticIV = generateDailyStaticKeyAndIV()
    cipher_bytes = bytes.fromhex(hex_data)
    decrypted = aes_decrypt(cipher_bytes, staticKey, staticIV)
    return decrypted.decode("utf-8")


# =============================
# LAYER 2 (Key-Derived IV)
# =============================

def encryptWithKeyDerivedIV(plain_str, key_str):
    key_bytes = key_str.encode("utf-8")
    derived_iv = key_bytes
    encrypted = aes_encrypt(plain_str.encode("utf-8"), key_bytes, derived_iv)
    return encrypted


def decryptWithKeyDerivedIV(cipher_bytes, key_str):
    key_bytes = key_str.encode("utf-8")
    derived_iv = key_bytes
    decrypted = aes_decrypt(cipher_bytes, key_bytes, derived_iv)
    return decrypted.decode("utf-8")


# =============================
# REQUEST BODY
# =============================

def encryptRequestBody(plainText, keyOverride=None):
    keyString = keyOverride if keyOverride is not None else defaultKey

    inner = encryptWithDailyStaticKey(plainText)
    outer = encryptWithKeyDerivedIV(inner, keyString)

    return base64.b64encode(outer).decode("utf-8")


def decryptRequestBody(ciphertext_b64, keyOverride=None):
    keyString = keyOverride if keyOverride is not None else defaultKey
    cipher_bytes = base64.b64decode(ciphertext_b64)
    return decryptWithKeyDerivedIV(cipher_bytes, keyString)


def decryptResponse(ciphertext_b64, keyOverride=None):
    return decryptWithDailyStaticKey(
        decryptRequestBody(ciphertext_b64, keyOverride)
    )


# =============================
# RANDOM REQUEST KEY (Exact JS behavior)
# =============================

def generateRequestKey():
    f = [
        "0","1","2","3","4","5","6","7","8","9",
        "A","B","C","D","E","F","G","H","I","J",
        "K","L","M","N","O","P","Q","R","S","T",
        "U","V","W","X","Y","Z",
        "a","b","c","d","e","f","g","h","i","j",
        "k","l","m","n","o","p","q","r","s","t",
        "u","v","w","x","y","z"
    ]

    result = []
    for _ in range(16):
        index = math.ceil(61 * __import__("random").random())
        result.append(f[index])

    return "".join(result)


async def post(baseURL, endpoint, payload, authCookie):
    # Note: endpoint SHOULDN'T begin with a /
    # Generate random request key
    randomKey = generateRequestKey()
    encryptedKey = encryptWithDailyStaticKey(randomKey)
    encryptedBody = encryptRequestBody(json.dumps(payload), randomKey)

    headers = {
        "Content-Type": "application/json",
        "X-Sign-Source": "CC",
        "X-Sign-Key": encryptedKey,
        "X-Device-Id": "84801afb787791d3d0e39bd27730f99a",
        "X-Device-Type": "web",
        "X-Device-Telegram": "",
        "X-Device-Scene": "online",
        "Cookie": f"Authorization={authCookie}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{baseURL}{endpoint}",
                headers=headers,
                content=encryptedBody
            )
        response.raise_for_status()

        response_json = response.json()

        # Preserve JS bug (defaultKey instead of randomKey)
        decrypted_response = decryptResponse(response_json, defaultKey)

        print("Decrypted Response:", decrypted_response)
        return decrypted_response

    except Exception as e:
        print("Error in POST request:", e)
        return None