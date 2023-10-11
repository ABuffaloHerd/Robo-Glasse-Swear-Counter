import json
import os

def init_config(servers):
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            file = {}
            for server in servers:
                file[server] = {"alerts" : False}

            json.dump(file, f)


def get_config(server):
    with open('config.json', 'r') as f:
        return json.load(f)[server]
    
def is_alerts(server):
    try:
        return get_config(server)['alerts']
    except KeyError:
        # Server not in config.json, add it
        with open('config.json', 'r') as f:
            data = json.load(f)
            data[server] = {"alerts" : False}

def set_alerts(server, value : bool):
    with open('config.json', 'r') as f:
        data = json.load(f)
        data[server]['alerts'] = value
    with open('config.json', 'w') as f:
        json.dump(data, f)