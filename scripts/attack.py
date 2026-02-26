from typing import Dict, Union
import asyncio
import time
from post import post
from coin import CryptoCoin
import hashlib
from utils import extractUserId
import logging


logger = logging.getLogger(__name__)

class CWalletClient:
    def __init__(self, authCookie: str, payPassCode: str):
        self.authCookie = authCookie
        self.payPass = hashlib.md5(payPassCode.encode('utf-8')).hexdigest()
        self.baseURL = "https://my.cwallet.com/cctip/v1/"
        self._withdraw_lock = asyncio.Lock()
        self._execution_semaphore = asyncio.Semaphore(10)  # limits total concurrent executions

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
        await asyncio.sleep(1)
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



    async def executeFullTransaction(self, targetAddress: str, amount: str, cryptoCoin: CryptoCoin) -> str:
        async with self._execution_semaphore:
            logger.debug("Starting executeFullTransaction")
            logger.debug("Target address: %s | Amount: %s | Coin: %s", targetAddress, amount, cryptoCoin.symbol)
            
            try:
                # Step 1
                logger.debug("Step 1: Checking internal address")
                isInner = await self.checkInnerAddress(targetAddress, cryptoCoin)

                if not isInner:
                    logger.warning("Address is not internal. Aborting transaction.")
                    return None

                logger.debug("Address confirmed as internal")

                # Step 2 - 6 (critical section)
                async with self._withdraw_lock:
                    await asyncio.sleep(5)
                    logger.debug("Step 2: Generating new bill ID")
                    billId = await self.generateNewBillId()
                    logger.debug("Generated billId: %s", billId)

                    logger.debug("Step 3: Making transaction")
                    txResult = await self.makeTransaction(targetAddress, billId, amount, cryptoCoin)
                    logger.debug("Transaction result: %s", txResult)

                    # Step 4
                    logger.debug("Step 4: Fetching transaction ID")
                    txId = await self.getTransactionId(txResult["bill_id"], txResult["type"])
                    logger.debug("Transaction ID: %s", txId)

                    # Step 5
                    logger.debug("Step 5: Creating transaction share link")
                    link = await self.createTransactionShareLink(txId)
                    logger.debug("Share link created: %s", link)

                    # Step 6
                    logger.debug("Step 6: Canceling transaction")
                    await self.cancelTransaction(txResult["bill_id"], txResult["type"])
                    logger.debug("Transaction canceled successfully")

                # Step 7
                logger.debug("Step 7: Getting user ID from share link")
                userId = await self.getTransactionShareLinkUserId(txId)
                logger.debug("Extracted userId: %s", userId)

                return userId
            
            except Exception as e:
                print(e)
                return None
        

    async def filterInnerAddresses(self, addresses: list[str], cryptoCoin: CryptoCoin) -> list[str]:
        semaphore = asyncio.Semaphore(5)  # limit concurrent requests
        counter = 0
        async def limited_check(address: str) -> bool:
            nonlocal counter
            async with semaphore:
                counter += 1
                try:
                    print(f"Proccessing address number {counter}")
                    return await self.checkInnerAddress(address, cryptoCoin)
                except Exception as e:
                    print(f"Error in number {counter} : {e}")
                    return False
        tasks = [limited_check(addr) for addr in addresses]
        results = await asyncio.gather(*tasks)

        # keep only addresses that returned True
        return [addr for addr, is_inner in zip(addresses, results) if is_inner]
