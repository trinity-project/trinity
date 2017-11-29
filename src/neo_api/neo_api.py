'''
This neo api python implementation

'''


import requests
import json
from . import api_error


class NeoApi(object):
    """
    neo api
    """

    def __init__(self, url,rcpversion, id=1):
        self.url = url
        self.version = rcpversion
        self.id = id

    def post_request(self, payload):
        json_payload = json.dumps(payload)
        result = requests.post(self.url, json=json_payload)
        if result.status_code != requests.codes.ok:
            raise result.raise_for_status()
        else:
            return result

    def getaccountstate(self, address):
        """
        :param
            address : string, asset address, startswith A. length 34, e.g. "AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz"

        request payload:
        {
          "jsonrpc": "2.0",
          "method": "getaccountstate",
          "params": ["AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz"],
          "id": 1
        }
        response:
        {
           "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "version": 0,
                "script_hash": "1179716da2e9523d153a35fb3ad10c561b1e5b1a",
                "frozen": false,
                "votes": [],
                "balances": [
                    {
                       "asset": "c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b",
                       "value": "94"
                   }
                ]
            }
        }

        script_hash: contract script hash
        frozen: bool, check if contract frozen
        votes:  query the NEO for vote
        balance: asset balance
        asset : asset ID
        value: amount of assets
        """
        payload = {
                "jsonrpc": self.version,
                "method": "getaccountstate",
                "params": [address],
                "id": self.id
        }

        if isinstance(address, str) and len(address) == 34:
            return self.post_request(self.payload)
        else:
            raise api_error.APIParamError(self.address)

    def getassetstate(self, asset_id):
        """

        :param
            asset_id: string, asset ID , e.g. for NEO: "c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"
                NeoGas："602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"
                can get from CLI command list asset to get the other asset ID
        :return:

        request:
        {
            "jsonrpc": "2.0",
             "method": "getassetstate",
             "params": ["c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"],
             "id": 1
        }
        response:
        {
             "jsonrpc": "2.0",
             "id": 1,
             "result": {
                  "version": 0,
                   "id": "c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b",
                   "type": "SystemShare",
                    "name": [
                        {
                              "lang": "zh-CN",
                              "name": "小蚁股"
                        },
                        {
                             "lang": "en",
                              "name": "AntShare"
                         }
                    ],
                   "amount": "100000000",
                   "available": "100000000",
                   "precision": 0,
                   "owner": "00",
                   "admin": "Abf2qMs1pzQb8kYk9RuxtUb9jtRKJVuBJt",
                    "issuer": "Abf2qMs1pzQb8kYk9RuxtUb9jtRKJVuBJt",
                   "expiration": 2000000,
                   "frozen": false
                  }
        }
        """
        payload = payload = {
                "jsonrpc": self.version,
                "method": "getassetstate",
                "params": [asset_id],
                "id": self.id
        }
        return self.post_request(payload)

    def getbalance(self, asset_id):
        """
        Note: need open the wallet via Neo-CLI be for using this method
        :param
            asset_id: string, asset ID , e.g. for NEO: "c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"
                NeoGas："602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"
                can get from CLI command list asset to get the other asset ID
        :return:
        request:
        {
             "jsonrpc": "2.0",
             "method": "getbalance",
             "params": ["025d82f7b00a9ff1cfe709abe3c4741a105d067178e645bc3ebad9bc79af47d4"],
             "id": 1
        }
        response:
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "balance": "1.01",
                "confirmed": "1.01"
             }
        }
        balance: the real asset in the wallet
        confirmed: The exact amount of the asset in the wallet, where only confirmed amounts can be used for transfer.

        Balance and Confirmed values may not be equal. This happens when there is an output transaction from the wallet,
        and the change has not been confirmed yet, so the confirmed value will be less than the balance.
        Once the deal is confirmed, the two will become equal.
        """
        payload = {
             "jsonrpc": self.version,
             "method": "getbalance",
             "params": ["asset_id"],
             "id": 1
        }

        return self.post_request(payload)

    def getbestblockhash(self):
        """

        :return:
        request:
        {
             "jsonrpc": "2.0",
             "method": "getbestblockhash",
             "params": [],
             "id": 1
        }
        response:
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": "773dd2dae4a9c9275290f89b56e67d7363ea4826dfd4fc13cc01cf73a44b0d0e"
        }
        result: The hash of the tallest block in the main chain.
        """
        payload = {
            "jsonrpc": self.version,
            "method": "getbestblockhash",
            "params": [],
            "id": self.id
        }
        return self.post_request(payload)



