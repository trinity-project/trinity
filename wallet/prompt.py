#!/usr/bin/env python3

import os
import sys
pythonpath = os.path.dirname(os.path.dirname(__file__))
sys.path.append(pythonpath)


import argparse
import json

import traceback

from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.shortcuts import print_tokens
from prompt_toolkit.token import Token
from twisted.internet import reactor, task, endpoints
from log import LOG
from lightwallet.Settings import settings

from wallet.utils import get_arg,to_aes_key
from wallet.Interface.rpc_interface import RpcInteraceApi
from twisted.web.server import Site
from lightwallet.prompt import PromptInterface
from wallet.ChannelManagement.channel import create_channel, filter_channel_via_address,\
    get_channel_via_address,chose_channel,close_channel
from wallet.TransactionManagement import message as mg
from wallet.TransactionManagement import transaction as trinitytx
from wallet.Interface.rpc_interface import MessageList
import time
from sserver.model.base_enum import EnumChannelState

from wallet.Interface import gate_way
from wallet.configure import Configure

from functools import reduce
from wallet.BlockChain.monior import monitorblock,Monitor

GateWayIP = Configure.get("GatewayIP")
Version = Configure.get("Version")




class UserPromptInterface(PromptInterface):
    Channel = False

    def __init__(self):
        super().__init__()
        user_commands = ["channel enable","channel create {partner} {asset_type} {deposit}",
                         "channel tx {receiver} {asset_type} {count}",
                         "channel close {peer},"
                         "channel peer"]
        self.commands.extend(user_commands)

    def get_address(self):
        """

        :return:
        """
        wallet = self.Wallet.ToJson()
        try:
            account =  wallet.get("accounts")[0]
            return account["address"], account["pubkey"]
        except AttributeError:
            return None,None


    def run(self):
        """
        :return:
        """

        tokens = [(Token.Neo, 'TRINITY'), (Token.Default, ' cli. Type '),
                  (Token.Command, "'help' "), (Token.Default, 'to get started')]

        print_tokens(tokens,self.token_style)
        print("\n")


        while self.go_on:
            try:
                result = prompt("trinity>",
                                history=self.history,
                                get_bottom_toolbar_tokens=self.get_bottom_toolbar,
                                style=self.token_style,
                                # refresh_interval=15
                                )
            except EOFError:
                return self.quit()
            except KeyboardInterrupt:
                self.quit()
                continue

            try:
                command, arguments = self.parse_result(result)

                if command is not None and len(command) > 0:
                    command = command.lower()

                    if command == 'quit' or command == 'exit':
                        self.quit()
                    elif command == 'help':
                        self.help()
                    elif command == 'wallet':
                        self.show_wallet(arguments)
                    elif command is None:
                        print('please specify a command')
                    elif command == 'create':
                        self.do_create(arguments)
                    elif command == 'close':
                        self.do_close_wallet()
                    elif command == 'open':
                        self.do_open(arguments)
                    elif command == 'export':
                        self.do_export(arguments)
                    elif command == 'wallet':
                        self.show_wallet(arguments)
                    elif command == 'send':
                        self.do_send(arguments)
                    elif command == 'tx':
                        self.show_tx(arguments)
                    elif command == 'channel':
                        self.do_channel(arguments)
                    else:
                        print("command %s not found" % command)

            except Exception as e:

                print("could not execute command: %s " % e)
                traceback.print_stack()
                traceback.print_exc()


    def quit(self):
        print('Shutting down. This may take about 15 sec to sync the block info')
        self.go_on = False
        Monitor.stop_monitor()
        self.do_close_wallet()
        reactor.stop()

    def do_channel(self,arguments):
        if not self.Wallet:
            print("Please open a wallet")
            return
        command = get_arg(arguments)

        if command == 'create':
            if not self.Channel:
                self._channel_noopen()
            assert len(arguments) == 4
            if not self.Wallet:
                raise Exception("Please Open The Wallet First")
            partner = get_arg(arguments, 1)
            asset_type = get_arg(arguments, 2)
            deposit = int(get_arg(arguments, 3).strip())
            create_channel(self.Wallet.url, partner,asset_type, deposit)

        elif command == "enable":
            self.Wallet.address, self.Wallet.pubkey = self.get_address()
            result = gate_way.join_gateway(self.Wallet.pubkey).get("result")
            if result:
                self.Wallet.url = json.loads(result).get("MessageBody").get("Url")
                self.Channel = True
                print("Channel Function Enabled")
            else:
                self._channel_noopen()

        elif command == "tx":
            if not self.Channel:
                self._channel_noopen()
            receiver = get_arg(arguments,1)
            asset_type = get_arg(arguments,2)
            count = get_arg(arguments,3)

            receiverpubkey,receiverip= receiver.split("@")
            channels = filter_channel_via_address(self.Wallet.url,receiver, EnumChannelState.OPENED.name)
            ch = chose_channel(channels,self.Wallet.url.split("@")[0].strip(), count, asset_type)
            channel_name = ch.channel
            gate_way_ip = self.Wallet.url.split("@")[1].strip()

            if channel_name:
                tx_nonce = trinitytx.TrinityTransaction(channel_name, self.Wallet).get_latest_nonceid()
                mg.RsmcMessage.create(channel_name,self.Wallet,self.Wallet.pubkey,
                                      receiverpubkey, int(count), receiverip, gate_way_ip, str(tx_nonce+1), asset_type="TNC")
            else:
                message = {"MessageType":"QueryRouter",
                           "Sender":self.Wallet.url,
                            "Receiver": receiver,
                           "MessageBody":{
                               "AssetType":asset_type,
                               "Value":count
                               }
                           }
                router = gate_way.get_router_info(message)
                if router:
                    r = router.get("FatherPath")
                    n = router.get("Next")
                    fee = reduce(lambda x, y:x+y,[int(i[1]) for i in r])
                    answer = prompt("will use fee %s , Do you still want tx? [Yes/No]> " %(str(fee)))
                    if answer.upper() == "YES":
                        tx_nonce = trinitytx.TrinityTransaction(channel_name, self.Wallet).get_latest_nonceid()
                        mg.RsmcMessage.create(channel_name, self.Wallet, self.Wallet.pubkey,
                                              receiverpubkey, int(count), receiverip, gate_way_ip, str(tx_nonce + 1),
                                              asset_type="TNC",router= r, next_router=n)
                    else:
                        return None
                else:
                    return

        elif command == "close":
            if not self.Channel:
                self._channel_noopen()
            channel_name = get_arg(arguments, 1)
            print("Closing channel {}".format(channel_name))
            if channel_name:
                close_channel(channel_name, self.Wallet)
            else:
                print("No Channel Create")

        elif command == "peer":
            if not self.Channel:
                self._channel_noopen()
            get_channel_via_address(self.Wallet.url)
            return

    def _channel_noopen(self):
        print("Channel Function Can Not be Opened at Present")
        return

    def handlemaessage(self):
        while self.go_on:
            if MessageList:
                message = MessageList.pop(0)
                self._handlemessage(message[0])
            time.sleep(0.1)

    def _handlemessage(self,message):
        LOG.info("Handle Message: <---- {}".format(json.dumps(message)))
        if isinstance(message,str):
            message = json.loads(message)
        try:
            message_type = message.get("MessageType")
        except AttributeError:
            return "Error Message"
        if message_type == "Founder":
            m_instance = mg.FounderMessage(message, self.Wallet)
        elif message_type in [ "FounderSign" ,"FounderFail"]:
            m_instance = mg.FounderResponsesMessage(message, self.Wallet)
        elif message_type == "Htlc":
            m_instance = mg.HtlcMessage(message, self.Wallet)
        elif message_type == "Rsmc":
            m_instance = mg.RsmcMessage(message, self.Wallet)
        elif message_type in ["RsmcSign", "RsmcFail"]:
            m_instance = mg.RsmcResponsesMessage(message, self.Wallet)
        elif message_type == "Settle":
            m_instance = mg.SettleMessage(message, self.Wallet)
        elif message_type in ["SettleSign","SettleFail"]:
            m_instance = mg.SettleResponseMessage(message, self.Wallet)
        elif message_type == "RegisterChannel":
            m_instance = mg.RegisterMessage(message, self.Wallet)
        elif message_type == "CreateTranscation":
            m_instance = mg.CreateTranscation(message, self.Wallet)
        elif message_type == "TestMessage":
            m_instance = mg.TestMessage(message, self.Wallet)
        else:
            return "No Support Message Type "

        return m_instance.handle_message()


def main():
    parser = argparse.ArgumentParser()
    # Show the  version
    parser.add_argument("--version", action="version",
                        version=Version)
    parser.add_argument("-m", "--mainnet", action="store_true", default=False,
                        help="Use MainNet instead of the default TestNet")
    parser.add_argument("-p", "--privnet", action="store_true", default=False,
                        help="Use PrivNet instead of the default TestNet")

    args = parser.parse_args()

    if args.mainnet:
        settings.setup_mainnet()
    elif args.privnet:
        settings.setup_privnet()
    else:
        settings.setup_testnet()


    UserPrompt = UserPromptInterface()
    api_server_rpc = RpcInteraceApi("20556")
    endpoint_rpc = "tcp:port={0}:interface={1}".format("20556", "0.0.0.0")
    endpoints.serverFromString(reactor, endpoint_rpc).listen(Site(api_server_rpc.app.resource()))


    reactor.suggestThreadPoolSize(15)
    reactor.callInThread(UserPrompt.run)
    reactor.callInThread(UserPrompt.handlemaessage)
    reactor.callInThread(monitorblock)
    reactor.run()

if __name__ == "__main__":
    main()
