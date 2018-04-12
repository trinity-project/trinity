
import json
import os
import logging
from json.decoder import JSONDecodeError
from neocore.Cryptography import Helper

import logzero


DIR_CURRENT = os.path.dirname(os.path.abspath(__file__))
DIR_PROJECT_ROOT = os.path.abspath(os.path.join(DIR_CURRENT, ".."))



ADDRESS_VERSION=23

NEO="0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"
GAS="0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"
TNC="0x0c34a8fd0109df360c7cf7ca454404901db77f5e"

headers = {
    "Content-Type": "application/json"
}

NODEURL="http://localhost:8888"