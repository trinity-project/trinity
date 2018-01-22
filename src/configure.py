import json
import os
Configure_file = os.path.join(os.path.dirname(__file__),"configure.json")

with open(Configure_file,'r') as f:
    Configure = json.load(f)