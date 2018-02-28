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