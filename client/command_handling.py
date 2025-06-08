import json
import re
from time import sleep


class CommandHandler:
    def __init__(self,client):
        self.client = client
        self.commands = [
            (re.compile(r'^login\s+(\w+)\s+(\w+)$'), lambda m: self.login(m.group(1), m.group(2))),
            (re.compile(r'^exit$'), lambda m: self.exit_client()),
            (re.compile(r'^exit\s+server$'), lambda m: self.exit_server()),
            (re.compile(r'^signup\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)$'), lambda m: self.sign_up(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7), m.group(8))),
            #signup (type) (first name) (last name) (username) (password) (access personnel) (access nuclear) (access bio)
        ]
    def handle_command(self, command):
        for pattern, handler in self.commands:

            match = pattern.match(command)
            if match:
                return handler(match)
        return False

    def login(self, username, password):
        req_json = {
            'type': 'login',
            'username': username,
            'password': password
        }
        req = json.dumps(req_json)
        return req

    def sign_up(self, user_type, first_name, last_name, username, password, access_p, access_n, access_b):
        req_json = {
            'type': 'signup',
            'username': username,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'user_type': user_type,
            'access_p': access_p,
            'access_n': access_n,
            'access_b': access_b
        }
        req = json.dumps(req_json)
        return req

    def exit_client(self):
        self.client.rsp_handler.running = False
        sleep(1.1)
        req_json = {
            'type': 'exit_client',
        }
        req = json.dumps(req_json)
        return req

    def exit_server(self):
        self.client.rsp_handler.running = False
        sleep(1.1)
        req_json = {
            'type': 'exit_server',
        }
        req = json.dumps(req_json)
        return req

