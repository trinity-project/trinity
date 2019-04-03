"""Author: Trinity Core Team 

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""


from twisted.internet import reactor, protocol
from wallet.TransactionManagement.message import Message
from wallet.BlockChain.monior import Monitor
from wallet.configure import Configure
from wallet.Interface.gate_way import join_gateway
from wallet.Interface.rpc_interface import CurrentLiveWallet
from log import LOG


class GatwayClientProtocol(protocol.Protocol):
    """Once connected, send a message, then print the result."""
    printlog = True

    def connectionMade(self):
        self.transport.setTcpNoDelay(True)
        message = {
                   "MessageType": "RegisterKeepAlive",
                   "Ip":          "{}:{}".format(Configure.get("NetAddress"),Configure.get("NetPort")),
                   "Protocol":"TCP",
                  }
        self.transport.write(encode_bytes(message))
        Message.Connection = True
        Monitor.BlockPause = False
        if CurrentLiveWallet.Wallet:
            join_gateway(CurrentLiveWallet.Wallet.pubkey)
        else:
            pass
        print("Connect the Gateway")
        GatwayClientProtocol.printlog = True

    def senddata(self, message):
        print("send", message)
        self.transport.write(encode_bytes(message))



class GatwayClientFactory(protocol.ClientFactory):

    def __init__(self):
        self.protocol = None

    def _handle_connection_lose(self, connector):
        Message.Connection = False
        Monitor.BlockPause = True
        connector.connect()
        GatwayClientProtocol.printlog=False


    def clientConnectionLost(self, connector, reason):
        if GatwayClientProtocol.printlog:
            print('Lost Gateway')
            LOG.error(reason)
        self._handle_connection_lose(connector)



    def clientConnectionFailed(self, connector, reason):
        if GatwayClientProtocol.printlog:
            print('Can Not connect Gateway, Please Check the gateway')
            LOG.error(reason)
        self._handle_connection_lose(connector)

    def buildProtocol(self, addr):
        self.protocol = GatwayClientProtocol ()
        return self.protocol


def encode_bytes(data):
    """
    encode python obj to bytes data\n
    :return: bytes type
    """
    import json
    import struct
    from gateway.config import cg_bytes_encoding
    if type(data) != str:
        data = json.dumps(data)
    # data = _add_end_mark(data)
    version = 0x000001
    cmd = 0x000065
    bdata = data.encode(cg_bytes_encoding)
    header = [version, len(bdata), cmd]
    header_pack = struct.pack("!3I", *header)
    return header_pack + bdata



if __name__ == '__main__':
    import json
    factory =  GatwayClientFactory()
    t = reactor.connectTCP("localhost", 8189,factory)
    def handle_message(factory):
        msg_dic= {"SyncWalletData":{"MessageType": "SyncWalletData",
                "NetMagic": "1111111111",
              "Sender":"xxxxxxx@ip:port",
                "MessageBody": {
                   "Publickey": "000000000000000000000000000000000000000000000",
                    "alias": "bob",
                    "AutoCreate": True,
                    "Ip": "10.10.10.1:2000",
                    "MaxChannel": 20,
                   "Channel": {# channel configure ,
        "TNC":{
            "CommitMinDeposit": 1,   # the min commit deposit
            "CommitMaxDeposit": 5000,# the max commit deposit
            "Fee": 0.01 # gateway fee
        },
        "NEO": {
            "Fee": 0    # must be integer
        },
        "GAS": {
            "Fee": 0.001
        },
                   "Balance": {"tnc":20}},
               }},
                  }

        print(json.dumps(msg_dic,indent=4))
        while True:
            if factory.protocol and factory.protocol.connected:

                msg_index = input(":")
                msg = msg_dic.get(msg_index)
                if msg:
                    factory.protocol.senddata(msg)
                else:
                    continue

    reactor.callInThread(handle_message,factory)
    reactor.run()
