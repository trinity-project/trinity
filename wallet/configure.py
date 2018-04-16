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
    "alias":"TrinityNode",# you can rename your node
    "GatewayURL":"http://localhost:8077",
    "Fee": 0.01,
     "AutoCreate": True, # if the wallet accept the create channel request automatically
    "CommitMinDeposit": 0,  # the min commit deposit
     "MaxChannel":100,# the max number to create channel, if 0 , no limited
    "AssetType":{
        "TNC": "0x849d095d07950b9e56d0c895ec48ec5100cfdff1"
    },
    "BlockChain":{
        "RPCClient":"http://localhost:20332", # neocli client json-rpc
        "NeoProtocol":"/home/will/neocli/protocol.json",
    },
    "DataBase":{"url": "http://localhost:20554"
    },
    "Version":"v0.2.1"
}