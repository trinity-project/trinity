from .neo_api import neo_api
from configure import Configure


NeoServer = neo_api.NeoApi(Configure["BlockNet"])

def add_to_channel(address, type, public_key, signature, channel_name, deposit=0, open_block_number=10 ):
        return True


def setting_transection(sender, receiver, channel_name):
    return True


def send_raw_transection(hax):
    #return NeoServer.sendrawtransaction(hax)
    return True


def NewTransection(asset_type,from_addr, to_addr, count):
    print("Signature")
    return ""


def get_balance(address, asset_type):
    return [{"AssetType":"TNC",
            "Balance":10000},
            {"AssetType":"NEO",
            "Balance":10000},
            {"AssetType":"NEOGAS",
            "Balance":10000}]




