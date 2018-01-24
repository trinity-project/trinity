"""
Minimal NEO node with custom code in a background thread.

It will log events from all smart contracts on the blockchain
as they are seen in the received blocks.
"""
import threading
import json
from time import sleep, time
import requests
from logzero import logger
from twisted.internet import reactor, task
from neo.Network.NodeLeader import NodeLeader
from neo.Core.Blockchain import Blockchain
from neo.Implementations.Blockchains.LevelDB.LevelDBBlockchain import LevelDBBlockchain
from neo.Settings import settings

from model import Session, Vout, LocalBlockCout


# If you want the log messages to also be saved in a logfile, enable the
# next line. This configures a logfile with max 10 MB and 3 rotations:
# settings.set_logfile("/tmp/logfile.log", max_bytes=1e7, backup_count=3)


def custom_background_code():
    """ Custom code run in a background thread.

    This function is run in a daemonized thread, which means it can be instantly killed at any
    moment, whenever the main thread quits. If you need more safety, don't use a  daemonized
    thread and handle exiting this thread in another way (eg. with signals and events).
    """

    def get_block_count():
        chain_block_count = Blockchain.Default().Height
        return chain_block_count

    def get_block_txs(index):
        block = Blockchain.Default().GetBlock(str(index))
        if block is not None:
            return block.ToJson()["tx"]
        return None

    def get_tx_info(txId):
        tx_data, height = Blockchain.Default().GetTransaction(txId)
        if height > -1:
            tx_info = tx_data.ToJson()
            return tx_info
        return None

    session = Session()
    localBlockCount = session.query(LocalBlockCout).all()
    if localBlockCount:
        localBlockCountInstace = localBlockCount[0]
        local_block_count = localBlockCountInstace.height
    else:
        local_block_count = 0
        localBlockCountInstace = LocalBlockCout(height=0)
        session.add(localBlockCountInstace)
        session.commit()

    logger.info("Block %s/ %s ", local_block_count, str(Blockchain.Default().HeaderHeight))
    t1 = int(time())

    while True:
        t2 = int(time())
        tx = t2 - t1
        if tx == 3:
            t1 = t2
            logger.info("Block %s/ %s ", local_block_count, str(Blockchain.Default().HeaderHeight))
        chain_block_count = get_block_count()
        if local_block_count < chain_block_count - 1:
            txs = get_block_txs(local_block_count)
            if len(txs) > 1:
                for tx in txs[1:]:
                    tx_info = get_tx_info(tx)
                    if tx_info:

                        for number, vout in enumerate(tx_info["vout"]):
                            vout = Vout(tx_id=tx_info["txid"], address=vout["ScriptHash"], asset_id=vout["AssetId"],
                                        vout_number=number, value=vout["Value"])
                            session.add(vout)
                            session.commit()

                        for vin in tx_info["vin"]:
                            class_instacce = session.query(Vout).filter(Vout.tx_id == vin["txid"],
                                                                        Vout.vout_number == vin["vout"]).one()
                            if class_instacce:
                                # print ("delete vout tx_id:{0} ".format(class_instacce.tx_id))
                                session.delete(class_instacce)
                                session.commit()

            local_block_count += 1
            localBlockCountInstace.height = local_block_count
            session.add(localBlockCountInstace)
            session.commit()

        else:
            sleep(15)
            logger.info("Block %s/ %s ", local_block_count, str(Blockchain.Default().HeaderHeight))


def main():
    # Setup the blockchain
    blockchain = LevelDBBlockchain(settings.LEVELDB_PATH)
    Blockchain.RegisterBlockchain(blockchain)
    dbloop = task.LoopingCall(Blockchain.Default().PersistBlocks)
    dbloop.start(.1)
    NodeLeader.Instance().Start()

    # Start a thread with custom code
    d = threading.Thread(target=custom_background_code)
    d.setDaemon(True)  # daemonizing the thread will kill it when the main thread is quit
    d.start()

    # Run all the things (blocking call)
    reactor.run()
    logger.info("Shutting down.")


if __name__ == "__main__":
    main()
