import socket
import threading
import json
import sqlite3
import os
import time
from users import User
from cryptography.fernet import Fernet



class ClientHandler(threading.Thread):
    def __init__(self, client_socket, address, server_instance):
        super().__init__()
        self.client_socket = client_socket
        self.address = address
        self.server_instance = server_instance
        self.is_running = True

        self.user = User()

    def run(self):
        self.db_conn = sqlite3.connect(r'database\imf.sqlite')
        self.cursor = self.db_conn.cursor()
        print(f'client handler thread started: {self.address}')
        self.client_socket.settimeout(self.server_instance.timeout)
        try:

            while self.is_running:
                msg = self.client_socket.recv(1024).decode()
                if msg:
                    data = json.loads(msg)
                    print(f"data received: {data}")
                    response_data = None
                    match data['type']:
                        case 'login':
                            response_data = self.server_instance.handle_login(self, data["username"], data["password"])


                        case 'exit_client':
                            self.stop()
                        case 'exit_server':
                            self.server_instance.shutdown()
                        case 'signup':
                            response_data = self.server_instance.handle_signup(self, data)
                        case 'logout':
                            self.user = User()
                        case 'file_lists':
                            response_data = self.server_instance.handle_file_lists(self)
                        case 'download_file':
                            # rsp = {"type": "download_file","file_name": data['file_name'] ,"file_size": os.path.getsize(f"database/files/{data['file_type']}/{data['file_name']}")}
                            # response = json.dumps(rsp)
                            # self.client_socket.send(response.encode())

                            # time.sleep(0.1)
                            filepath = os.path.join("database", "files", data['file_type'], data['file_name'])
                            if os.path.exists(filepath) and os.path.isfile(filepath):
                                try:
                                    with open(filepath, "rb") as file:
                                        file_data = file.read()  # Read in chunks
                                    file_data_dec = self.server_instance.master_fernet.decrypt(file_data)
                                    response_data = {'type':'file_data', 'file_name': data['file_name'], 'file_type': data['file_type'] , "status":"success",  'data': file_data_dec.hex()}
                                    print("sent file")
                                except Exception as e:
                                    print(f"Exception on sendfile: {str(e)}")
                            else:
                                response_data = {'type':'file_data', 'file_name': data['file_name'], 'file_type': data['file_type'] , 'status':'failed'}
                                print("path/file not exist")
                        case 'update_files':
                            response_data = self.server_instance.handle_update_files(self, data)
                        case 'send_chat_message':
                            self.server_instance.handle_send_chat_message(self, data)
                        case 'request_chat_history':
                            response_data = self.server_instance.handle_request_chat_history(self, data)
                        case 'create_chat':
                            response_data = self.server_instance.handle_create_chat(self, data)
                        case 'update_chat_list':
                            response_data = self.server_instance.handle_update_chat_list(self, data)
                        case 'delete_file':
                            response_data = self.server_instance.handle_delete_file(self, data)

                    if response_data:
                        print(f"response sent: {response_data}")
                        response = json.dumps(response_data)
                        self.client_socket.sendall(response.encode())
        except socket.timeout:
            pass
        except ConnectionResetError:
            print("ConnectionResetError")
        except Exception as e:
            print(f"Exception: {e}")
        finally:
            self.stop()

    def stop(self):
        if self.user.username:
            offline_announcement = {"type": "user_offline", "username": self.user.username}
        self.is_running = False
        print(f'client handler thread stopped: {self.address}')
        try:
            self.client_socket.close()
            self.db_conn.close()
        except Exception as e:
            print(f"Exception: {e}")

    def login_user(self, user_id, username, hashed_password, first_name, last_name, user_type, personnel_files_access, nuclear_codes_access, biological_files_access):
        #TODO if user_type = "agent":
        #     do this
        self.user = User(user_id=user_id, username=username, hashed_password=hashed_password, first_name=first_name, last_name=last_name, personnel_files_access=personnel_files_access, nuclear_codes_access=nuclear_codes_access, biological_files_access=biological_files_access)

