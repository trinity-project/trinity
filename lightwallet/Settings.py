
import json
import os
import logging
from json.decoder import JSONDecodeError
from neocore.Cryptography import Helper






class SettingsHolder:

    headers = {
        "Content-Type": "application/json"
    }

    DIR_CURRENT = os.path.dirname(os.path.abspath(__file__))
    ADDRESS_VERSION = 23

    NEO = "0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"
    GAS = "0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"
    TNC = "0x0c34a8fd0109df360c7cf7ca454404901db77f5e"


    NODEURL = None
    NET_NAME = None



    def setup_mainnet(self):
        self.NET_NAME = "MainNet"
        self.NODEURL = "https://neoapi.trinity.ink"
        self.TNC = "0x08e8c4400f1af2c20c28e0018f29535eb85d15b6"
    def setup_testnet(self):
        self.NET_NAME = "TestNet"
        self.NODEURL = "http://neoapi-testnet.trinity.ink:21332"
        self.TNC = "0x849d095d07950b9e56d0c895ec48ec5100cfdff1"
    def setup_privnet(self):
        self.NET_NAME = "PrivateNet"
        self.NODEURL = "http://localhost:8888"
        self.TNC = "0x0c34a8fd0109df360c7cf7ca454404901db77f5e"



settings = SettingsHolder()


