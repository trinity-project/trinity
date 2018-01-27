import pymysql
import requests
from flask import Flask, jsonify
from mysqlhander import  MysqlHander
from flask import  request
from transfer_tnc import create_tx

localhost_database = {
    'host': 'localhost',
    'db': 'testnet_account_info',
    'user': 'root',
    'passwd': 'root',
    'charset':'utf8',
    'cursorclass':pymysql.cursors.DictCursor
}


hander= MysqlHander(localhost_database)


app = Flask(__name__)



@app.route('/api/getBalance',methods=["POST"])
def get_balance():
    args=request.json
    address=args.get("address")
    hander.cursor.execute('SELECT * FROM balance where address="{0}"'.format(address))
    balance=hander.cursor.fetchone()
    if balance:
        response={
            "gasBalance":float(balance["gas_balance"]),
            "neoBalance":float(balance["neo_balance"]),
        }
    else:
        response={}
    return jsonify(response)

@app.route('/api/getNeoVout', methods=["POST"])
def get_neo_vout():
    args = request.json
    address = args.get("address")
    hander.cursor.execute('SELECT * FROM neo_vout where address="{0}"'.format(address))
    neo_vouts = hander.cursor.fetchall()

    if neo_vouts:
        response = neo_vouts
    else:
        response = []
    return jsonify(response)


@app.route('/api/getGasVout', methods=["POST"])
def get_gas_vout():
    args = request.json
    address = args.get("address")
    hander.cursor.execute('SELECT * FROM gas_vout where address="{0}"'.format(address))
    gas_vouts = hander.cursor.fetchall()
    if gas_vouts:
        response = [{
            "txId":item.get("tx_id"),
            "voutNumber":item.get("vout_number"),
            "value":float(item.get("value"))
        }
                    for item in gas_vouts]
    else:
        response = []
    return jsonify(response)



@app.route('/api/contructTx', methods=["POST"])
def construct_tx():
    args = request.json
    address_to = args.get("address_to")
    address_from = args.get("address_from")
    tnc_amount = args.get("amount")
    contract_hash=args.get("contract_hash")
    hander.cursor.execute('SELECT * FROM balance where address="{0}"'.format(address_from))
    balance=hander.cursor.fetchone()
    if balance:
        gas=float(balance["gas_balance"])
        if gas < 0.001:
            return jsonify({"code":1,"message":"no enough gas"})

        hander.cursor.execute('SELECT * FROM gas_vout where address="{0}"'.format(address_from))
        gas_vouts = hander.cursor.fetchall()
        if gas_vouts:
            for item in gas_vouts:
                if float(item.get("value"))>0.001:
                    input_txid = item.get("tx_id")[2:]
                    preIndex = item.get("vout_number")
                    gas_change = float(item.get("value"))- 0.001
                    tx_data=create_tx(contract_hash=contract_hash,address_from=address_from,
                                      address_to=address_to,tnc_amount=tnc_amount,gas_change=gas_change,
                                      input_txid=input_txid,preIndex=preIndex)


                    return jsonify({"code":0,"tx_data":tx_data})

        return jsonify({"code": 1, "message": "no enough gas"})
    else:
        return jsonify({"code": 1, "message": "no enough gas"})



@app.route('/api/sendRawtransaction', methods=["POST"])
def send_rawtransaction():
    args=request.json
    hexstr=args.get("sign_tx_data")
    url = "http://127.0.0.1:20332"
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "jsonrpc": "2.0",
        "method": "sendrawtransaction",
        "params": [hexstr],
        "id": 1
    }
    res = requests.post(url, headers=headers, json=data).json()
    if res["result"]:
        return jsonify({"code":0,"message":"sucess"})
    return jsonify({"code":1,"message":"fail"})


if __name__=="__main__":
    app.run(host="0.0.0.0")