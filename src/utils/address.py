import csv
from flask_jsonrpc.proxy import ServiceProxy

def get_address_wfi(address_file, wfi_file):
    server = ServiceProxy("http://localhost:10332")
    with open(wfi_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        with open (address_file) as f:
            for address in f:
                result = server.dumpprivkey(address)
                wfi = result.get("result")
                writer.writerow([address, wfi])





