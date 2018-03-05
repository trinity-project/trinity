import requests
import unittest
import json
import os
from channel_manager import manager


class CommonItem(object):
    def __init(self):
        pass

    @classmethod
    def from_dict(cls, common_dict):
        ret = cls()
        for k, v in common_dict.items():
            setattr(ret, k, v)
        return ret


class CommonResult(CommonItem):

    def __init__(self, json_dict):
        self.result = CommonItem.from_dict(json_dict)


class NeoTestApi(object):
    """
    neo api
    """

    def __init__(self, url, rcpversion="2.0", id=1):
        self.url = url
        self.version = rcpversion
        self.id = id

    def phase_request_result(self, common_result):
        if hasattr(common_result, "error"):
            print(common_result.error["message"])
        else:
            return common_result

    def print_result(self, result):
        print(json.dumps(result, indent=2))

    def post_request(self, payload):
        result = requests.post(self.url, json=payload)
        if result.status_code != requests.codes.ok:
            raise result.raise_for_status()
        else:
            print("Debug:", payload["method"])
            self.print_result(result.json())
            print("#" * 20)
            return self.phase_request_result(CommonResult(result.json()).result)

    def generate_payload(self, method, params):
        payload = {
            "jsonrpc": self.version,
            "method": method,
            "params": params,
            "id": self.id
        }
        return payload

    def test_registeraddress(self, address, port, pubkey):
        params = [address, port, pubkey]
        if isinstance(address, str):
            return self.post_request(self.generate_payload("registeaddress", params))
        else:
            raise APIParamError(address)

    def test_registchannle(self, sender_addr, receiver_addr, asset_type, deposit, open_blockchain):
        params = [sender_addr, receiver_addr, asset_type, deposit, open_blockchain]
        return self.post_request(self.generate_payload("registchannel", params))

    def test_getchannelstate(self, local_addr):
        return self.post_request(self.generate_payload("getchannelstate", [local_addr]))

    def test_sendrawtransaction(self, txdata, signature, publickey):
        return self.post_request(self.generate_payload("sendrawtransaction", [txdata, signature, publickey]))

    def test_sendertoreceiver(self, sender, receiver, channel_name, asset_type, count):
        return self.post_request(
            self.generate_payload("sendertoreceiver", [sender, receiver, channel_name, asset_type, count]))

    def test_close_channel(self, sender, receiver, channel_name):
        return self.post_request(
            self.generate_payload("closechannel", [sender, receiver, channel_name]))

    def test_get_history(self, channel_name, index, count):
        return self.post_request(self.generate_payload("gethistory",[channel_name, index, count]))


def mock_set_channel_open(channel_name):
    sender, receiver = manager.split_channel_name(channel_name)
    ch = manager.Channel(sender, receiver)
    ch.set_channel_open()


def mock_close_channel(channel_name):
    sender, receiver = manager.split_channel_name(channel_name)
    ch = manager.Channel(sender, receiver)
    ch.close()

class FunctionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testserver = NeoTestApi("http://localhost:5000")
        cls.address1 = ("ATiabWLxT5sLQpkppZDK9JmCF9wBFYpX3V",
                        "037e164ccc6b7e9db6d6c2d421c8ac13d4399e5408d27c017a6c871219899cb251")
        cls.address2 = ("AZLtmATYKJLJgdTEap1osSFTpfmnexBCLZ",
                        "036f7218f737e122d3aca71b7dc4136b666ccdbb8d82a77d171fb243eb1082dca9")
        cls.channel_name = None
        cls.raw_tx = None
        cls.contract_address = None

    def test001_register_address(self):
        for address in [self.address1, self.address2]:
            result = self.testserver.test_registeraddress(address=address[0], port="3001", pubkey=address[1])
            self.assertEqual(result.result, [0, 'SUCCESS'])

    def test002_register_channel(self):
        result = self.testserver.test_registchannle(sender_addr=self.address1[0], receiver_addr=self.address2[0],
                                                    asset_type="TNC", deposit=100, open_blockchain=1000)
        FunctionTest.channel_name = result.result["channel_name"]
        FunctionTest.contract_address = result.result["contract_address"]
        FunctionTest.raw_tx = result.result["trad_info"]

    def test003_get_channel_state(self):
        for address in [self.address1, self.address2]:
            result = self.testserver.test_getchannelstate(address[0])
            self.assertEqual(len(result.result["message"]), 1)
            message = result.result["message"][0]
            self.assertEqual(message["channel_state"], "State.OPENING")
            self.assertEqual(message["channel_name"], self.channel_name)
            self.assertEqual(len(message["tx_info"]), 2)
            tx_info =  message["tx_info"]
            for tx in tx_info:
                self.assertEqual(tx["balance"], 0)
                self.assertEqual(tx["deposit"], 0.0)
                self.assertTrue(tx["address"] in [self.address1[0], self.address2[0]])

    def test004_set_channel_open(self):
        mock_set_channel_open(self.channel_name)
        for address in [self.address1, self.address2]:
            result = self.testserver.test_getchannelstate(address[0])
            self.assertEqual(len(result.result["message"]), 1)
            message = result.result["message"][0]
            self.assertEqual(message["channel_state"], "State.OPEN")
            self.assertEqual(message["channel_name"], self.channel_name)
            self.assertEqual(len(message["tx_info"]), 2)
            tx_info =  message["tx_info"]
            t = [tx for tx in tx_info if tx["address"] == self.address1[0]][0]
            self.assertEqual(t["deposit"], 100.0)
            self.assertEqual(t["balance"], 100)
            t = [tx for tx in tx_info if tx["address"] == self.address2[0]][0]
            self.assertEqual(t["deposit"], 0.0)
            self.assertEqual(t["balance"], 0)


    def test005_set_send_to_receiver(self):
        result = self.testserver.test_sendertoreceiver(self.address1[0], self.address2[0], self.channel_name,
                                                       "TNC", 20)
        self.assertEqual(result.result, "SUCCESS")
        result = self.testserver.test_getchannelstate(self.address1[0])
        message = result.result["message"][0]
        tx_info = message["tx_info"]
        t = [tx for tx in tx_info if tx["address"]==self.address1[0]][0]
        self.assertEqual(t["deposit"],100.0)
        self.assertEqual(t["balance"], 80)
        t = [tx for tx in tx_info if tx["address"] == self.address2[0]][0]
        self.assertEqual(t["deposit"], 0.0)
        self.assertEqual(t["balance"], 20)

    def test006_get_history(self):
        result = self.testserver.test_get_history(self.channel_name, index=1,count=2)
        print(result.result)



    @classmethod
    def tearDownClass(cls):
        mock_close_channel(cls.channel_name)




if __name__ == "__main__":
    import time

    unittest.main()
