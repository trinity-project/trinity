import pymysql
from flask import Flask, jsonify
from mysqlhander import  MysqlHander
from flask import  request


localhost_database = {
    'host': 'localhost',
    'db': 'testnet_wallet',
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





app.run(host="0.0.0.0",port=8000,debug=True)