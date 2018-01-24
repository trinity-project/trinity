import requests
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
        if hasattr(self.result,"result") and isinstance(self.result.result, dict):
            self.result.result = CommonItem.from_dict(self.result.result)


class NeoApi(object):
    """
    neo api
    """

    def __init__(self, url, rcpversion="2.0", id=1):
        self.url = url
        self.version = rcpversion
        self.id = id

    def phase_request_result(self,common_result):
        if hasattr(common_result, "error"):
            print(common_result.error["message"])
        else:
            return common_result

    def post_request(self, payload):
        result = requests.post(self.url, json=payload)
        if result.status_code != requests.codes.ok:
            raise result.raise_for_status()
        else:
            print(result.json())

    def generate_payload(self, method, params):
        payload = {
            "jsonrpc": self.version,
            "method": method,
            "params": params,
            "id": self.id
        }
        return payload

    def test_registeraddress(self,address):
        params = [address]
        if isinstance(address, str):
            return self.post_request(self.generate_payload("registeaddress",params))
        else:
            raise APIParamError(address)

    def test_registchannle(self,sender_addr, receiver_addr, asset_type, deposit, open_blockchain):
        params = [sender_addr,receiver_addr,asset_type,deposit,open_blockchain]
        return self.post_request(self.generate_payload("registchannle",params))

    def test_getchannelstate(self,local_addr):
        return self.post_request(self.generate_payload("getchannelstate",[local_addr]))

    def test_sendrawtransaction(self,sender_addr, channel_name, signature):
        return self.post_request(self.generate_payload("sendrawtransaction",[sender_addr, channel_name, signature]))

    def test_sendertoreceiver(self,sender, receiver, channel_name, asset_type,count):
        return self.post_request(self.generate_payload("sendertoreceiver",[sender, receiver, channel_name, asset_type, count]))


if __name__ == "__main__":
    test= NeoApi("http://localhost:5000")
    result1 = test.test_registeraddress("AT5AVHBxp4TH5k5ni1x2m81P7HgaJUW8h8")
    result = test.test_registchannle("AT5AVHBxp4TH5k5ni1x2m81P7HgaJUW8h9","AT5eVHBxp4TH5k5ni1x2m81P7HgaJUW8h7","tnc","100","789087")
    result5 = test.test_registchannle("AT5eVHBxp4TH5k5ni1x2m81P7HgaJUW8h7","AT5AVHBxp4TH5k5ni1x2m81P7HgaJUW8h9","tnc","100","789087")
    result2= test.test_getchannelstate("AT5AVHBxp4TH5k5ni1x2m81P7HgaJUW8h9")
    result3=test.test_getchannelstate("AT5eVHBxp4TH5k5ni1x2m81P7HgaJUW8h7")
    result4= test.test_sendrawtransaction("AT5AVHBxp4TH5k5ni1x2m81P7HgaJUW8h9",'AATT55AeVVHHBBxxpp44TTHH55kk55nnii11xx22mm8811PP77HHggaaJJUUWW88hh97',"0xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    test.test_getchannelstate("AT5AVHBxp4TH5k5ni1x2m81P7HgaJUW8h9")
    test.test_sendertoreceiver("AT5AVHBxp4TH5k5ni1x2m81P7HgaJUW8h9","AT5eVHBxp4TH5k5ni1x2m81P7HgaJUW8h7",'AATT55AeVVHHBBxxpp44TTHH55kk55nnii11xx22mm8811PP77HHggaaJJUUWW88hh97',"tnc","20")



