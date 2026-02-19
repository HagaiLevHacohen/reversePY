from typing import Dict, Union
import time
from post import post
from coin import CryptoCoin
import hashlib
from utils import extractUserId

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
    

    async def getTransactionId(self, billId: str, type: int) -> str:
        endpoint = "user/transaction/newrecord"
        payload = {
            "type": type,
            "record_id": billId
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
                f"Failed to get transaction id: code={response.get('code')}, msg={response.get('msg')}"
            )
        return response["data"]["id"]
    

    async def createTransactionShareLink(self, transactionId: str) -> str:
        endpoint = "user/transaction/share/create"
        payload = {
            "record_id": transactionId,
            "tran_type": "Send",
            "share_url": f"https://cwallet.com/txn/{transactionId}"
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
                f"Failed to create transaction share link: code={response.get('code')}, msg={response.get('msg')}"
            )
        return response["data"] # returns cwallet transaction link: "https://s.cwallet.com/14oem2y"
    

    async def cancelTransaction(self,billId: str, type: int) -> None:
        endpoint = "account/asset/withdraw/cancel"
        payload = {
            "bill_id": billId,
            "type": type
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
                f"Failed to cancel transaction: code={response.get('code')}, msg={response.get('msg')}"
            )
        


    async def getTransactionShareLinkUserId(self, transactionId: str) -> str:
        endpoint = "user/transaction/share/get"
        payload = {
            "record_id": transactionId
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
                f"Failed to get transaction share link user id: code={response.get('code')}, msg={response.get('msg')}"
            )
        targetUserId = response["data"]["to"]
        userId = extractUserId(targetUserId)
        return userId
    

    async def getUserData(self, userId: str) -> str:
        endpoint = "account/other/user"
        payload = {
            "id": userId
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
                f"Failed to get user's data: code={response.get('code')}, msg={response.get('msg')}"
            )
        return response["data"]