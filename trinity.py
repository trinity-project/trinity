# --*-- coding : utf-8 --*--
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
import platform
import operator
import json
import os

# version x.y.z
#   This version will have same meaning as Linux
#       x -- Production version with big different feature
#       y -- Odd number means formal version, Even number means development version
#       z -- Count of fixing bugs
__version__ = '0.1.1'
__os_platform__ = platform.system().upper() if platform.system() else 'LINUX'
__running_mode__ = (0 == operator.imod(int(__version__.split('.')[1]), 2))
Configure_file = os.path.join(os.path.dirname(__file__), "Configure.json")
Console_log = False


with open(Configure_file, 'r') as f:
    CONFIGURE = json.load(f)

DATABASE_CONFIG = {
    'authentication': {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    },
    'type': os.getenv('DB_TYPE', 'mongodb'),
    'name': os.getenv('DB_NAME', 'trinity') if __running_mode__ else 'beta-database',
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', 27017))
}