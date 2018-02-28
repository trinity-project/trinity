

from flask import Flask
from flask_jsonrpc import JSONRPC
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask_cors import CORS
from NodeB.config import MYSQLDATABASE

pymysql.install_as_MySQLdb()

app = Flask(__name__)
cors = CORS(app, support_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' %(MYSQLDATABASE["user"],MYSQLDATABASE["passwd"],MYSQLDATABASE["host"],MYSQLDATABASE["db"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=True
db = SQLAlchemy(app)
jsonrpc = JSONRPC(app, "/")




from .controller import *

