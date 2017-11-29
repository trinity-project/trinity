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

    def generate_payloade(self, method, params):
        payload = {
            "jsonrpc": self.version,
            "method": method,
            "params": params,
            "id": self.id
        }
        return payload

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
        params = [address]
        if isinstance(address, str) and len(address) == 34:
            return self.post_request(self.generate_payloade("getaccountstate",params))
        else:
            raise api_error.APIParamError(address)

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
        params = [asset_id]
        return self.post_request(self.generate_payloade("getassetstate", params))

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
        params = [asset_id]
        return self.post_request(self.generate_payloade("getbalance", params))

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
        params = []
        return self.post_request("getbestblockhash", params)

    def getblock(self, index, verbose=0):
        """

        :param
            index: Block index (block height) = Number of blocks - 1.
            verbose: Optional, the default value of verbose is 0.
                     When verbose is 0, the serialized information of the block is returned, represented by a hexadecimal string.
                     If you need to get detailed information, you will need to use the SDK for deserialization.
                     When verbose is 1, detailed information of the corresponding block in Json format string, is returned

        :return:
        request:
        {
            "jsonrpc": "2.0",
            "method": "getblock",
            "params": [10000],
            "id": 1
         }
         response:
        {
            "jsonrpc": "2.0",
            "id": 1,
             "result": "00000000e990d39e3ff75327e42c3459a4300b7f7d88ce8e00e98b05aa4f183aa515ce53294d136abf69e02f49fc
             43e002a31ba2c702e062d8683a559032a03b1e9e909c50b6065810270000455444dcd50f2caa59e75d652b5d3827bf04c165bbe9e
             f95cca4bf5501fd4501405e31eb19b1feaeb27c3a5b95f568b9b256fefe0ea61f6296eb8af836c29597617fe81d23a8bf66309000e
             4c7568b7f43560f61e4ee6cd1f78a2a42f50a5008c240ccf73ce9f7f810273730bdfc786d346086a697cc06239e88e040ed2ec0583
             c7dbb6eccb8b8a74afbd75cfbaff06c051b7e82abe65f96f50a1673e1536f91a3d540618e43cce18c7c91b54b2a5e44ba1e4a71a8d
             d0af0ec95c8c4f05343e66129b150057a5f79399a92eda1226fddd254702ffc682309787ab241509b2244e410334070a5ac50d897b
             f39f98780f79fb1a2416c41dc2e202b4ad797bd0c70e2b57f1157c4ff5551ec6df58bec6244dc72a3f25cd1836e8cdd4c0d8c2e5ba
             7e2d8859b40ae80743c9a2a8e154671eb156266971439a9017e96ea072c848287a71b2d6a99a67ba50fc7935a6de4d8884794291fc
             6cebd77158954ef03b10d5d0a30b52bc9f1552102486fd15702c4490a26703112a5cc1d0923fd697a33406bd5a1c00e0013b09a702
             1024c7b7fb6c310fccf1ba33b082519d82964ea93868d67666 2d4a59ad548df0e7d2102aaec38470f6aad0042c6e877cfd8087d26
             76b0f516fddd362801b9bd3936399e2103b209fd4f53a7170ea4444e0cb0a6bb6a53c2bd016926989cf85f9b0fba17a70c2103b8d9
             d5771d8f513aa0869b9cc8d50986403b78c6da36890638c3d46a5adce04a2102ca0e27697b9c248f6f16e085fd0061e26f44da85b5
             8ee835c110caa5ec3ba5542102df48f60e8f3e01c48ff40b9b7f1310d7a8b2a193188befe1c2e3df740e89509357ae010000455444
             dc00000000 "
        }
        """
        if verbose not in [0,1]:
            raise api_error.APIParamError(verbose)
        else:
            params = [index, 1] if verbose else [index]
            return self.post_request("getblock", params)

    def getblockcount(self):
        """

        :return:
        request:
        {
            "jsonrpc": "2.0",
            "method": "getblockcount",
            "params":[],
            "id": 1
        }
        response:
        {
            "jsonrpc": "2.0",
            "id": 1,
             "result": 991991
         }
        """
        params = []
        return self.post_request(self.generate_payloade("getblockcount", params))

    def getblockhash(self, index):
        """

        :param
            index: Block index(block height)
        :return:

        request:
        {
            "jsonrpc": "2.0",
            "method": "getblockhash",
            "params": [10000],
            "id": 1
        }
        """
        params = [index]
        return self.post_request(self.generate_payloade("getblockhash", params))

    def getconnectioncount(self):
        """

        :return:
        request:
        {
            "jsonrpc": "2.0",
            "method": "getconnectioncount",
            "params":[],
            "id": 1
        }
        response:
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": 10
        }
        """
        params = []
        return self.post_request(self.generate_payloade("getconnectioncount",params))

    def getrawmempool(self):
        """

        :return:
        {
            "jsonrpc": "2.0",
            "method": "getrawmempool",
            "params":[],
            "id": 1
        }
        response:
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": [
                    "B4534f6d4c17cda008a76a1968b7fa6256cd90ca448739eae8e828698ccc44e7"
            ]
        }

        """
        params = []
        return self.post_request(self.generate_payloade("getrawmempool", params))

    def getrawtransaction(self, txid, verbose=0):
        """

        :param
            txid: Transaction ID
            verbose: Optional, the default value of verbose is 0.
             When verbose is 0, the serialized information of the block is returned, represented by a hexadecimal string.
             If you need to get detailed information, you will need to use the SDK for deserialization.
             When verbose is 1, detailed information of the corresponding block in Json format string, is returned.

        :return:

        request:
        {
             "jsonrpc": "2.0",
             "method": "getrawtransaction",
             "params": ["f4250dab094c38d8265acc15c366dc508d2e14bf5699e12d9df26577ed74d657"],
             "id": 1
        }
        response:
        {
             "jsonrpc": "2.0",
             "id": 1,
              "result": "80000001195876cb34364dc38b730077156c6bc3a7fc570044a66fbfeeea56f71327e8ab0000029b7cffdaa674
              beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc500c65eaf440000000f9a23e06f74cf86b8827a9108ec2e0f8
              9ad956c9b7cffdaa674beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc50092e14b5e00000030aab52ad93f6c
              e17ca07fa88fc191828c58cb71014140915467ecd359684b2dc358024ca750609591aa731a0b309c7fb3cab5cd0836ad3992a
              a0a24da431f43b68883ea5651d548feb6bd3c8e16376e6e426f91f84c58232103322f35c7819267e721335948d385fae5be66
              e7ba8c748ac15467dcca0693692dac"
        }

        """
        if verbose not in [0,1]:
            raise api_error.APIParamError(verbose)
        else:
            params = [txid, 1] if verbose else [txid]
            return self.post_request("getrawtransaction", params)

    def gettxout(self, txid, n=0):
        """

        :param
             txid: Transaction ID
             n: The index of the transaction output to be obtained in the transaction (starts from 0)
        :return:
        request:
        {
            "jsonrpc": "2.0",
            "method": "gettxout",
            "params": ["f4250dab094c38d8265acc15c366dc508d2e14bf5699e12d9df26577ed74d657", 0],
            "id": 1
        }
        response:
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
            "N": 0,
            "Asset": "c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b",
            "Value": "2950",
            "Address": "AHCNSDkh2Xs66SzmyKGdoDKY752uyeXDrt"
            }
        }

        """
        params = [txid, n]
        return self.post_request(self.generate_payloade("gettxout", params))

    def sendrawtransaction(self, hex):
        """

        :param
           hex: A hexadecimal string that has been serialized, after the signed transaction in the program.
        :return:

        request:
        {
            "jsonrpc": "2.0",
            "method": "sendrawtransaction",
            "params": [ "80000001195876cb34364dc38b730077156c6bc3a7fc570044a66fbfeeea56f71327e8ab0000029b7cffdaa674be
            ae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc500c65eaf440000000f9a23e06f74cf86b8827a9108ec2e0f89ad956
            c9b7cffdaa674beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc50092e14b5e00000030aab52ad93f6ce17ca07fa
            88fc191828c58cb71014140915467ecd359684b2dc358024ca750609591aa731a0b309c7fb3cab5cd0836ad3992aa0a24da431f4
            3b68883ea5651d548feb6bd3c8e16376e6e426f91f84c58232103322f35c7819267e721335948d385fae5be66e7ba8c748ac15467
            dcca0693692dac"],
            "id": 1
        }
        response:
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": false
        }
        """
        params = [hex]
        return self.post_request(self.generate_payloade("sendrawtransaction", params))

    def sendtoaddress(self, asset_id, address, value, fee=0):
        """

        :param
           asset_id: Asset ID (asset identifier), which is the transaction ID of the RegistTransaction when the asset is registered.
           address: Payment address
           value: Amount transferred
           fee: Fee, default value is 0 (optional parameter)

        :return:
        request:
        {
            "jsonrpc": "2.0",
            "method": "sendtoaddress",
            "params": ["025d82f7b00a9ff1cfe709abe3c4741a105d067178e645bc3ebad9bc79af47d4", "AK4if54jXjSiJBs6jkfZjxAastauJtjjse", 1],
            "id": 1
        }
        response:
        {
            "jsonrpc": "2.0",
            "id": 1,
             "result": {
                  "Txid": "fbd69da6996cc0896691a35cba2d3b2e429205a12307cd2bdea5fbdf78dc9925",
                  "Size": 262,
                  "Type": "ContractTransaction",
                  "Version": 0,
                  "Attributes":[],
                  "Vin": [
                     {
                        "Txid": "19fbe968be17f4bd7b7f4ce1d27e39c5d8a857bd3507f76c653d204e1e9f8e63",
                         "Vout": 0
                     }
                  ],
                  "Vout": [
                            {
                                "N": 0,
                                "Asset": "025d82f7b00a9ff1cfe709abe3c4741a105d067178e645bc3ebad9bc79af47d4",
                                "Value": "1",
                                 "Address": "AK4if54jXjSiJBs6jkfZjxAastauJtjjse"
                            },
                          {
                                "N": 1,
                                "Asset": "025d82f7b00a9ff1cfe709abe3c4741a105d067178e645bc3ebad9bc79af47d4",
                                "Value": "4978980",
                                "Address": "AK4if54jXjSiJBs6jkfZjxAastauJtjjse"
                          }
                  ],
                  "Sys_fee": "0",
                  "Net_fee": "0",
                  "Scripts": [
                       {
                           "Invocation": "40f02345c7e90245F085d0c588433ca9e89c6df58f3636b5240288aab5f081b1c67c3cad5946890de9001fcfe8d8b748b647b116891e6f1fb2393cc2f1aba45a81",
                            "Verification": "21027b30333e0d0e6552ae6d1da9f9409f551e35ee9719305e945dc4dcba998456caac"
                       }
                   ]
             }
        }
        """
        params = [asset_id, address, value, fee]
        return self.post_request(self.generate_payloade("sendtoaddress", params))

