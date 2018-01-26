from configure import Configure
import threading
from time import sleep
from logzero import logger


from twisted.internet import reactor, task

from neo.contrib.smartcontract import SmartContract
from neo.Network.NodeLeader import NodeLeader
from neo.Core.Blockchain import Blockchain
from neo.Implementations.Blockchains.LevelDB.LevelDBBlockchain import LevelDBBlockchain
from neo.Settings import settings

from channel_manager.channel import get_channelnames_via_address, Channel, State
from channel_manager.manager import close_channel
from utils.channel import split_channel_name
from crypto.Cryptography.Helper import hash_to_wallet_address,bytes_to_hex_string, hex2interger



smart_contract = SmartContract(Configure["TNC"].replace("0x",""))
ContractAddr = Configure["ContractAddr"]
DepositIN =[]
DepositOut = []

# Register an event handler for Runtime.Notify events of the smart contract.
@smart_contract.on_notify
def sc_notify(event):
    logger.info("SmartContract Runtime.Notify event: %s", event)

    if not len(event.event_payload):
        return

    logger.info("- payload part 1: %s", event.event_payload[0].decode("utf-8"))
    tx_type = event.event_payload[0]
    sender = hash_to_wallet_address(event.event_payload[1])
    receiver = hash_to_wallet_address(event.event_payload[2])
    value = hex2interger(bytes_to_hex_string(event.event_payload[3]))
    if not tx_type.decode() == "transfer":
        return
    if receiver == ContractAddr:
        depoist_in(address=sender,value=value)
    elif sender == ContractAddr:
        depoist_out(address=receiver, value=value)
    print("sc_notification")


def depoist_in(address, value):
    print("depost in")
    channel_name = get_channelnames_via_address(address)
    if channel_name:
        print(channel_name)
        sender, receiver = split_channel_name(channel_name)
        ch = Channel(sender, receiver)
        if address == sender and ch.stateinDB == State.OPENING and value == ch.sender_deposit_cache:
            ch.set_channel_open()
        elif address == receiver and ch.stateinDB == State.OPENING and value == ch.receiver_deposit_cache:
            ch.set_channel_open()
        else:
            return None
    else:
        return None
    return address


def depoist_out(address,value):
    channel_name = get_channelnames_via_address(address)
    if channel_name:
        sender, receiver = split_channel_name(channel_name)
        ch = Channel(sender, receiver)
        ch.close()
    else:
        return None
    return address


def custom_background_code():

    while True:
        logger.info("Block %s / %s", str(Blockchain.Default().Height), str(Blockchain.Default().HeaderHeight))
        sleep(15)


def main():
    # Setup the blockchain
    blockchain = LevelDBBlockchain(settings.LEVELDB_PATH)
    Blockchain.RegisterBlockchain(blockchain)
    dbloop = task.LoopingCall(Blockchain.Default().PersistBlocks)
    dbloop.start(.1)
    NodeLeader.Instance().Start()

    # Disable smart contract events for external smart contracts
    settings.set_log_smart_contract_events(False)

    # Start a thread with custom code
    d = threading.Thread(target=custom_background_code)
    d.setDaemon(True)  # daemonizing the thread will kill it when the main thread is quit
    d.start()

    # Run all the things (blocking call)
    logger.info("Everything setup and running. Waiting for events...")
    reactor.run()
    logger.info("Shutting down.")

if __name__ == "__main__":
    main()
