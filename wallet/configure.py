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
Configure = {
    "alias":"TrinityNode",# you can re-name your node
    "GatewayURL":"http://localhost:8077",#gateway url getway ip and port, please check your gateway configure file
    "AutoCreate": True, # if the wallet accept the create channel request automatically
    "Channel":{# channel configure ,
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
        }
    },#
    "MaxChannel":100, # the max number to create channel, if 0 , no limited
    "NetAddress":"localhost",# the wallet net address, if the wallet is deployed with the gateway
    "RpcListenAddress":"0.0.0.0", # wallet json rpc service listening address
    "NetPort":"20556", # wallet json rpc service port
    "GatewayTCP":"localhost:8089", # gateway tcp connection address
    "AssetType":{ # asset id , TNC mainnet asset id :0x08e8c4400f1af2c20c28e0018f29535eb85d15b6
        "TNC": "0x849d095d07950b9e56d0c895ec48ec5100cfdff1",
        "NEO": "0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b",
        "GAS": "0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7",
    },
    "BlockChain":{ # blockchain information
        "RPCClient":"http://localhost:20332", # neocli local client json-rpc
        "NeoProtocol":"/home/neocli/protocol.json", # neocli protocol file
        "NeoUrlEnhance": "http://neoapi-testnet.trinity.ink:21332", # enhanced neo cli rpc service
        "NeoNetUrl" : "http://neoapi-testnet.trinity.ink:20332" # neocli on-line rpc service
    },
    "DataBase":{"url": "http://localhost:20554" # mongodb url
    },
    "Version":"V0.2.9", # version information
    "Magic":{
        "Block":1953787457,
        "Trinity":19990331
    }
}