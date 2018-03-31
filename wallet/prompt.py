#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import psutil
import traceback
import logging
import sys
from logzero import logger
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.shortcuts import print_tokens
from prompt_toolkit.token import Token
from twisted.internet import reactor, task, endpoints
import gevent
from gevent import monkey
#monkey.patch_all()


from neo import __version__
from neo.Core.Blockchain import Blockchain
from neo.Implementations.Blockchains.LevelDB.LevelDBBlockchain import LevelDBBlockchain
from neo.Implementations.Notifications.LevelDB.NotificationDB import NotificationDB
from neo.Network.NodeLeader import NodeLeader

from neo.Settings import settings, PrivnetConnectionError, PATH_USER_DATA
from neo.UserPreferences import preferences
from wallet.BlockChain.monior import monitorblock
from neo.Prompt.Utils import get_arg
from wallet.Interface.rpc_interface import RpcInteraceApi
from twisted.web.server import Site
from neo.bin.prompt import PromptInterface
from wallet.ChannelManagement.channel import create_channel, get_channel_name_via_address
from wallet.TransactionManagement import message as mg
from wallet.TransactionManagement import transaction as trinitytx
from wallet.Interface.rpc_interface import MessageList
import time
from neo.Implementations.Wallets.peewee.UserWallet import UserWallet

from neo.Wallets.utils import to_aes_key
from wallet.Interface import gate_way
from wallet.configure import Configure
GateWayIP = Configure.get("GatewayIP")
from functools import reduce


# Logfile settings & setup
LOGFILE_FN = os.path.join(PATH_USER_DATA, 'prompt.log')
LOGFILE_MAX_BYTES = 5e7  # 50 MB
LOGFILE_BACKUP_COUNT = 3  # 3 logfiles history
settings.set_logfile(LOGFILE_FN, LOGFILE_MAX_BYTES, LOGFILE_BACKUP_COUNT)

# Prompt history filename
FILENAME_PROMPT_HISTORY = os.path.join(PATH_USER_DATA, '.prompt.py.history')



class UserPromptInterface(PromptInterface):
    Channel = False

    def __init__(self):
        super().__init__()
        user_commands = ["channel open","channel create {partner} {asset_type} {deposit}",
                         "channel tx {receiver} {asset_type} {count}",
                         "channel close {channel_name},"
                         "channel show {channel_name}"]
        self.commands.extend(user_commands)

    def get_address(self):
        wallets = self.Wallet.ToJson()
        try:
            wallet = wallets["public_keys"][0]
            return wallet["Address"], wallet["Public Key"]
        except AttributeError:
            return None,None


    def run(self):
        dbloop = task.LoopingCall(Blockchain.Default().PersistBlocks)
        dbloop.start(.1)

        tokens = [(Token.Neo, 'NEO'), (Token.Default, ' cli. Type '),
                  (Token.Command, '\'help\' '), (Token.Default, 'to get started')]

        print_tokens(tokens, self.token_style)
        print('\n')

        while self.go_on:

            try:
                result = prompt("neo> ",
                                completer=self.get_completer(),
                                history=self.history,
                                get_bottom_toolbar_tokens=self.get_bottom_toolbar,
                                style=self.token_style,
                                refresh_interval=3
                                )
            except EOFError:
                # Control-D pressed: quit
                return self.quit()
            except KeyboardInterrupt:
                # Control-C pressed: do nothing
                continue

            try:
                command, arguments = self.input_parser.parse_input(result)

                if command is not None and len(command) > 0:
                    command = command.lower()

                    if command == 'quit' or command == 'exit':
                        self.quit()
                    elif command == 'help':
                        self.help()
                    elif command == 'create':
                        self.do_create(arguments)
                    elif command == 'open':
                        self.do_open(arguments)
                    elif command == 'build':
                        self.do_build(arguments)
                    elif command == 'load_run':
                        self.do_load_n_run(arguments)
                    elif command == 'import':
                        self.do_import(arguments)
                    elif command == 'export':
                        self.do_export(arguments)
                    elif command == 'wallet':
                        self.show_wallet(arguments)
                    elif command == 'send':
                        self.do_send(arguments)
                    elif command == 'sign':
                        self.do_sign(arguments)
                    elif command == 'block':
                        self.show_block(arguments)
                    elif command == 'tx':
                        self.show_tx(arguments)
                    elif command == 'header':
                        self.show_header(arguments)
                    elif command == 'account':
                        self.show_account_state(arguments)
                    elif command == 'asset':
                        self.show_asset_state(arguments)
                    elif command == 'contract':
                        self.show_contract_state(arguments)
                    elif command == 'testinvoke':
                        self.test_invoke_contract(arguments)
                    elif command == 'withdraw_request':
                        self.make_withdraw_request(arguments)
                    elif command == 'withdraw':
                        self.do_withdraw(arguments)
                    elif command == 'notifications':
                        self.do_notifications(arguments)
                    elif command == 'mem':
                        self.show_mem()
                    elif command == 'nodes' or command == 'node':
                        self.show_nodes()
                    elif command == 'state':
                        self.show_state()
                    elif command == 'debugstorage':
                        self.handle_debug_storage(arguments)
                    elif command == 'config':
                        self.configure(arguments)
                    elif command is None:
                        print("Please specify a command")
                    elif command == 'channel':
                        self.do_channel(arguments)
                    else:
                        print("Command %s not found" % command)

            except Exception as e:

                print("Could not execute command: %s" % e)
                traceback.print_stack()
                traceback.print_exc()

    def do_open(self, arguments):
        if self.Wallet:
            self.do_close_wallet()

        item = get_arg(arguments)

        if item and item == 'wallet':

            path = get_arg(arguments, 1)

            if path:

                if not os.path.exists(path):
                    print("Wallet file not found")
                    return

                passwd = prompt("[password]> ", is_password=True)
                password_key = to_aes_key(passwd)

                try:
                    self.Wallet = UserWallet.Open(path, password_key)

                    self._walletdb_loop = task.LoopingCall(self.Wallet.ProcessBlocks)
                    self._walletdb_loop.start(1)

                    print("Opened wallet at %s" % path)
                except Exception as e:
                    print("Could not open wallet: %s" % e)

            else:
                print("Please specify a path")
        else:
            print("Please specify something to open")

    def quit(self):
        print('Shutting down. This may take a bit...')
        self.go_on = False
        self.do_close_wallet()
        reactor.crash()

    def do_channel(self,arguments):
        if not self.Wallet:
            print("Please open a wallet")
            return
        self.Wallet.address, self.Wallet.pubkey = self.get_address()
        self.Wallet.url = "{}@{}".format(self.Wallet.pubkey,GateWayIP)
        command = get_arg(arguments)
        print(command)
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
        elif command == "open":
            walletHeight = self.Wallet.LoadStoredData("Height")
            blockHeight = Blockchain.Default().HeaderHeight
            # For Debug
            result = gate_way.join_gateway(self.Wallet.pubkey)
            print(result)
            self.Channel = True
            """
            if int(walletHeight) >= int(blockHeight)-10:
                if gate_way.join_gateway(self.Wallet.pubkey):
                    self.Channel = True
            else:
                self._channel_noopen()"""
        elif command == "tx":
            receiver = get_arg(arguments,1)
            asset_type = get_arg(arguments,2)
            count = get_arg(arguments,3)

            receiverpubkey , receiverip= receiver.split("@")
            channel_name = get_channel_name_via_address(self.Wallet.pubkey,receiverpubkey )

            if channel_name:
                tx_nonce = trinitytx.TrinityTransaction(channel_name, self.Wallet).get_latest_nonceid()
                mg.RsmcMessage.create(channel_name,self.Wallet,self.Wallet.pubkey,
                                      receiverpubkey, int(count), receiverip, str(tx_nonce+1), asset_type="TNC")
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
                                              receiverpubkey, int(count), receiverip, str(tx_nonce + 1),
                                              asset_type="TNC",router= r, next_router=n)
                    else:
                        return None
                else:
                    return

    def _channel_noopen(self):
        print("Please waite the block async")

    def get_completer(self):

        standard_completions = ['block', 'tx', 'header', 'mem', 'neo', 'gas',
                                    'help', 'state', 'nodes', 'exit', 'quit',
                                    'config', 'import', 'export', 'open',
                                    'wallet', 'contract', 'asset', 'wif',
                                    'watch_addr', 'contract_addr', 'testinvoke', 'tkn_send',
                                    'tkn_mint', 'tkn_send_from', 'tkn_approve', 'tkn_allowance',
                                    'build', 'notifications','channel' ]

        if self.Wallet:
            for addr in self.Wallet.Addresses:
                if addr not in self._known_things:
                    self._known_things.append(addr)
            for alias in self.Wallet.NamedAddr:
                if alias.Title not in self._known_things:
                    self._known_things.append(alias.Title)
            for tkn in self.Wallet.GetTokens().values():
                if tkn.symbol not in self._known_things:
                        elf._known_things.append(tkn.symbol)

        all_completions = standard_completions + self._known_things

        completer = WordCompleter(all_completions)

        return completer

    def handlemaessage(self):
        while True:
            if MessageList:
                message = MessageList.pop()
                #try:
                self._handlemessage(message)
                #except Exception as e:
                    #print(e)
            time.sleep(0.3)

    def _handlemessage(self,message):
        message = json.dumps(message)
        print("Receive Message： ",message)
        try:
            message_type = message.get("MessageType")
        except AttributeError:
            return "Error Message"
        if message_type == "Founder":
            m_instance = mg.FounderMessage(message, self.Wallet)
        elif message_type == "FounderSign":
            m_instance = mg.FounderResponsesMessage(message, self.Wallet)
        elif message_type == "Htlc":
            m_instance = mg.HtlcMessage(message, self.Wallet)
        elif message_type == "Rsmc":
            m_instance = mg.RsmcMessage(message, self.Wallet)
        elif message_type == "RegisterChannel":
            m_instance = mg.RegisterMessage(message, self.Wallet)
        elif message_type == "CreateTranscation":
            m_instance = mg.CreateTranscation(message, self.Wallet)
        elif message_type == "TestMessage":
            m_instance = mg.TestMessage(message, self.Wallet)
        else:
            return "No Message Type Fould"

        return m_instance.handle_message()

def main():
    parser = argparse.ArgumentParser()

    # Network group
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-m", "--mainnet", action="store_true", default=False,
                       help="Use MainNet instead of the default TestNet")
    group.add_argument("-p", "--privnet", nargs="?", metavar="host", const=True, default=False,
                       help="Use a private net instead of the default TestNet, optionally using a custom host (default: 127.0.0.1)")
    group.add_argument("--coznet", action="store_true", default=False,
                       help="Use the CoZ network instead of the default TestNet")
    group.add_argument("-c", "--config", action="store", help="Use a specific config file")

    # Theme
    parser.add_argument("-t", "--set-default-theme", dest="theme",
                        choices=["dark", "light"],
                        help="Set the default theme to be loaded from the config file. Default: 'dark'")

    # Verbose
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Show smart-contract events by default")

    # Where to store stuff
    parser.add_argument("--datadir", action="store",
                        help="Absolute path to use for database directories")

    # Show the neo-python version
    parser.add_argument("--version", action="version",
                        version="neo-python v{version}".format(version=__version__))

    args = parser.parse_args()

    # Setup depending on command line arguments. By default, the testnet settings are already loaded.
    if args.config:
        settings.setup(args.config)
    elif args.mainnet:
        settings.setup_mainnet()
    elif args.privnet:
        try:
            settings.setup_privnet(args.privnet)
        except PrivnetConnectionError as e:
            logger.error(str(e))
            return
    elif args.coznet:
        settings.setup_coznet()

    if args.theme:
        preferences.set_theme(args.theme)

    if args.verbose:
        settings.set_log_smart_contract_events(True)

    if args.datadir:
        settings.set_data_dir(args.datadir)

    # Instantiate the blockchain and subscribe to notifications
    blockchain = LevelDBBlockchain(settings.chain_leveldb_path)
    Blockchain.RegisterBlockchain(blockchain)

    UserPrompt = UserPromptInterface()


    if NotificationDB.instance():
        NotificationDB.instance().start()

    api_server_rpc = RpcInteraceApi("20556")
    endpoint_rpc = "tcp:port={0}:interface={1}".format("20556", "0.0.0.0")
    endpoints.serverFromString(reactor, endpoint_rpc).listen(Site(api_server_rpc.app.resource()))

    reactor.suggestThreadPoolSize(15)
    reactor.callInThread(UserPrompt.run)
    reactor.callInThread(UserPrompt.handlemaessage)
    reactor.callInThread(monitorblock)
    NodeLeader.Instance().Start()
    reactor.run()

    NotificationDB.close()
    Blockchain.Default().Dispose()
    NodeLeader.Instance().Shutdown()


if __name__ == "__main__":
    main()
