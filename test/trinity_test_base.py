# utf-8
import requests
import json


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
        if hasattr(self.result, "result") and isinstance(self.result.result, dict):
            self.result.result = CommonItem.from_dict(self.result.result)


class NeoApi(object):
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

    def post_request(self, payload):
        result = requests.post(self.url, json=payload)
        if result.status_code != requests.codes.ok:
            raise result.raise_for_status()
        else:
            self.print_result(result.json()["result"])
            return result.json()

    def print_result(self, result):
        print(json.dumps(result, indent=2))

    def generate_payload(self, method, params):
        payload = {
            "jsonrpc": self.version,
            "method": method,
            "params": params,
            "id": self.id
        }
        return payload

    def test_registeraddress(self, address):
        params = [address]
        if isinstance(address, str):
            return self.post_request(self.generate_payload("registeaddress", params))
        else:
            raise APIParamError(address)

    def test_registchannle(self, sender_addr, receiver_addr, asset_type, deposit, open_blockchain):
        params = [sender_addr, receiver_addr, asset_type, deposit, open_blockchain]
        return self.post_request(self.generate_payload("registchannle", params))

    def test_getchannelstate(self, local_addr):
        return self.post_request(self.generate_payload("getchannelstate", [local_addr]))

    def test_sendrawtransaction(self, sender_addr, channel_name, signature):
        return self.post_request(self.generate_payload("sendrawtransaction", [sender_addr, channel_name, signature]))

    def test_sendertoreceiver(self, sender, receiver, channel_name, asset_type, count):
        return self.post_request(
            self.generate_payload("sendertoreceiver", [sender, receiver, channel_name, asset_type, count]))

    def test_updatedeposit(self, local_addr, channel_name, asset_type, value):
        return self.post_request(self.generate_payload("updatedeposit", [local_addr, channel_name, asset_type, value]))

    def test_closechannel(self, sender_addr, receiver_addr, channel_name):
        return self.post_request(self.generate_payload("closechannel", [sender_addr, receiver_addr, channel_name]))


if __name__ == "__main__":
    test = NeoApi("http://106.15.91.150:20552")
    print(" 分别查询通道信息  预期 根据实际情况确定")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 清除channel 预期 第一步如果存在 删除成功  第一步如果不存在 删除失败")
    result = test.test_closechannel("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ", "AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7",
                                     "AAZMjQH9jL5PYRm732nKCuwXc1YbQtVUYJi9EQd142KvHJNuFbhWjfm1pRNaJgzwTrJ7")
    assert(result["result"]=="SUCCESS")
    print(" 分别查询通道信息  预期为空")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 一个地址注册 预期返回成功")
    result1 = test.test_registeraddress("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    print(" 分别查询通道信息  预期为空")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 另一个地址注册 预期返回成功")
    result1 = test.test_registeraddress("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 分别查询通道信息  预期为空")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 一方发起新建状态通道 并上缴押金  预期返回待签名的交易信息")
    result = test.test_registchannle("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ",
                                     "AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7", "tnc", "100", "789087")
    print(" 分别查询通道信息 预期为  获取到状态通道信息  押金 余额 都为0 ， 通道状态为opening")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 发送带签名交易信息 预期返回成功")
    result4 = test.test_sendrawtransaction("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ",
                                           'AAZMjQH9jL5PYRm732nKCuwXc1YbQtVUYJi9EQd142KvHJNuFbhWjfm1pRNaJgzwTrJ7',
                                           "0xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print(" 分别查询通道信息 预期为  获取到状态通道信息  一方押金 余额 都为0 ，另一方押金 余额都为押金值， 通道状态为open")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 另一方更新押金 上缴押金  预期返回待签名的交易信息")
    result = test.test_updatedeposit("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7",
                                     'AAZMjQH9jL5PYRm732nKCuwXc1YbQtVUYJi9EQd142KvHJNuFbhWjfm1pRNaJgzwTrJ7',
                                     "tnc", "100")
    print(" 分别查询通道信息 预期为  获取到状态通道信息   一方押金 余额 都为0 ，另一方押金 余额都为押金值， 通道状态为open")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 发送带签名交易信息 预期返回成功")
    result4 = test.test_sendrawtransaction("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7",
                                           'AAZMjQH9jL5PYRm732nKCuwXc1YbQtVUYJi9EQd142KvHJNuFbhWjfm1pRNaJgzwTrJ7',
                                           "0xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print(" 分别查询通道信息 预期为  获取到状态通道信息  押金 都为100 余额都为100， 通道状态为open")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 一方发起链下交易给对方转账20 预期返回成功")
    test.test_sendertoreceiver("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ", "AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7",
                               'AAZMjQH9jL5PYRm732nKCuwXc1YbQtVUYJi9EQd142KvHJNuFbhWjfm1pRNaJgzwTrJ7',
                               "tnc", "20")
    print(" 分别查询通道信息 预期为  获取到状态通道信息  押金 都为100 余额发送方剩余80，余额接收方剩余为120 通道状态为open")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 另一方发起链下交易给对方转账20 预期返回成功")
    test.test_sendertoreceiver("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7", "AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ",
                               'AAZMjQH9jL5PYRm732nKCuwXc1YbQtVUYJi9EQd142KvHJNuFbhWjfm1pRNaJgzwTrJ7',
                               "tnc", "20")
    print(" 分别查询通道信息 预期为  获取到状态通道信息  押金 余额 都为100 ， 通道状态为open")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")

    print(" 原端更新押金 上缴押金  预期返回待签名的交易信息")
    result = test.test_updatedeposit("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ",
                                     'AAZMjQH9jL5PYRm732nKCuwXc1YbQtVUYJi9EQd142KvHJNuFbhWjfm1pRNaJgzwTrJ7',
                                     "tnc", "100")
    print(" 分别查询通道信息 预期为  获取到状态通道信息  押金 余额 都为100 ， 通道状态为open")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 发送带签名交易信息 预期返回成功")
    result4 = test.test_sendrawtransaction("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ",
                                           'AAZMjQH9jL5PYRm732nKCuwXc1YbQtVUYJi9EQd142KvHJNuFbhWjfm1pRNaJgzwTrJ7',
                                           "0xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print(" 分别查询通道信息 预期为  获取到状态通道信息  源端押金 余额 都为200  目的端押金余额都为100， 通道状态为open")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 一方发起链下交易给对方转账20 预期返回成功")
    test.test_sendertoreceiver("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ", "AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7",
                               'AAZMjQH9jL5PYRm732nKCuwXc1YbQtVUYJi9EQd142KvHJNuFbhWjfm1pRNaJgzwTrJ7',
                               "tnc", "20")
    print(" 分别查询通道信息 预期为  获取到状态通道信息  源端押金 都为200 余额 180 目的端押金100 余额120 通道状态为open")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
    print(" 另一方发起链下交易给对方转账20 预期返回成功")
    test.test_sendertoreceiver("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7", "AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ",
                               'AAZMjQH9jL5PYRm732nKCuwXc1YbQtVUYJi9EQd142KvHJNuFbhWjfm1pRNaJgzwTrJ7',
                               "tnc", "20")
    print("分别查询通道信息 预期为  获取到状态通道信息  源端押金 余额 都为200 ， 目的端 押金 余额 为100 通道状态为open")
    result2 = test.test_getchannelstate("AZjHj5Ym3nCwcYQVYiEd4KHNFhjmpNJzTJ")
    result2 = test.test_getchannelstate("AMQ9LPR72KuX1btUJ9Q12vJubWf1Ragwr7")
