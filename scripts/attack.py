import base64
import json
import httpx
import asyncio
from typing import Dict, Union
import time
from post import post
from coin import CryptoCoin
import hashlib

class CWalletClient:
    def __init__(self, authCookie: str, payPassCode: str):
        self.authCookie = authCookie
        self.payPass = hashlib.md5(payPassCode.encode('utf-8')).hexdigest()
        self.baseURL = "https://my.cwallet.com/cctip/v1/"

    async def checkInnerAddress(self, address: str, cryptoCoin: CryptoCoin) -> bool:
        endpoint = "account/asset/withdraw/check"
        payload = {
            "chain_id": cryptoCoin.chainId,
            "contract": cryptoCoin.contract,
            "address": address,
            "memo": cryptoCoin.memo,
            "amount": "",
            "submit_type": 1
        }

        response = await post(
            self.baseURL,
            endpoint,
            payload,
            self.authCookie
        )
        if response["code"] != 10000:
            # Raise an exception if the API call failed
            raise ValueError(
                f"Failed to check address: code={response.get('code')}, msg={response.get('msg')}"
            )
        if response["data"]["is_inner_tx"]:
            return True
        else:
            return False
    

    async def generateNewBillId(self) -> str:
        endpoint = "account/asset/withdraw/new"
        payload = {}
        response = await post(
            self.baseURL,
            endpoint,
            payload,
            self.authCookie
        )
        if response["code"] != 10000:
            # Raise an exception if the API call failed
            raise ValueError(
                f"Failed to generate new bill id: code={response.get('code')}, msg={response.get('msg')}"
            )
        return response["data"]
    

    async def makeTransaction(self, targetAddress:str, billId: str, amount:str, cryptoCoin: CryptoCoin) -> Dict[str, Union[str, int]]:
        endpoint = "account/asset/withdraw/submit"
        timestamp_ms = int(time.time() * 1000)
        payload = {
            "bill_id": billId,
            "symbol": cryptoCoin.symbol,
            "address": targetAddress,
            "value": amount,
            "timestamp": timestamp_ms,
            "pay_pass": self.payPass,
            "fee": "0", # Since it's an internal transaction
            "chain_id": cryptoCoin.chainId,
            "contract": cryptoCoin.contract,
            "invoice": targetAddress,
            "memo": cryptoCoin.memo,
            "submit_type": 1,
            "remarks": "",
            "passkey_request_id": ""
        }
        response = await post(
            self.baseURL,
            endpoint,
            payload,
            self.authCookie
        )
        if response["code"] != 10000:
            # Raise an exception if the API call failed
            raise ValueError(
                f"Failed to submit transaction: code={response.get('code')}, msg={response.get('msg')}"
            )
        return response["data"] # returns {"bill_id":"202602190918562024413382663700480","type":3}