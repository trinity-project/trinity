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

import json
from json.decoder import JSONDecodeError
from klein import Klein
from wallet.Interface.rpc_utils import json_response, cors_header
from wallet.ChannelManagement import channel
from wallet.TransactionManagement import transaction
from log import LOG

MessageList = []


class RpcError(Exception):


    message = None
    code = None

    def __init__(self, code, message):
        super(RpcError, self).__init__(message)
        self.code = code
        self.message = message

    @staticmethod
    def parseError(message=None):
        return RpcError(-32700, message or "Parse error")

    @staticmethod
    def methodNotFound(message=None):
        return RpcError(-32601, message or "Method not found")

    @staticmethod
    def invalidRequest(message=None):
        return RpcError(-32600, message or "Invalid Request")

    @staticmethod
    def internalError(message=None):
        return RpcError(-32603, message or "Internal error")


class RpcInteraceApi(object):
    app = Klein()
    port = None

    def __init__(self, port):
        self.port = port

    #
    # JSON-RPC API Route
    #
    @app.route('/')
    @json_response
    @cors_header
    def home(self, request):
        body = None
        request_id = None

        try:
            body = json.loads(request.content.read().decode("utf-8"))
            request_id = body["id"] if body and "id" in body else None

            if "jsonrpc" not in body or body["jsonrpc"] != "2.0":
                raise RpcError.invalidRequest("Invalid value for 'jsonrpc'")

            if "id" not in body:
                raise RpcError.invalidRequest("Field 'id' is missing")

            if "method" not in body:
                raise RpcError.invalidRequest("Field 'method' is missing")

            params = body["params"] if "params" in body else None
            result = self.json_rpc_method_handler(body["method"], params)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }

        except JSONDecodeError as e:
            error = RpcError.parseError()
            return self._error_payload(request_id, error.code, error.message)

        except RpcError as e:
            return self._error_payload(request_id, e.code, e.message)

        except Exception as e:
            error = RpcError.internalError(str(e))
            return self._error_payload(request_id, error.code, error.message)

    def _error_payload(self, request_id, code, message):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": code,
                    "message": message
                }
            }

    def json_rpc_method_handler(self, method, params):

        if method == "SendRawtransaction":
            return transaction.TrinityTransaction.sendrawtransaction(params[0])

        #Todo
        #elif method ==  "QueryHistory":
            #return transaction.querytransaction(params)

        elif method == "TransactionMessage":
            return MessageList.append(params)

        elif method == "ConstrutInitChannelTransction":
            return transaction.construt_init_channel_transction(params)

        elif method == "ConstrutUpdateChannelTransction":
            return transaction.construt_update_channel_transction(params)

