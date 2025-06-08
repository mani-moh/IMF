import bcrypt
from cryptography.fernet import Fernet
import socket
import threading
from client_handling import ClientHandler
import json, os
import security


def requires_permission(permission):
    def decorator(func):
        def wrapper(self, handler):
            user = handler.user
            if permission == "personnel_files":
                if not user.personnel_files_access:
                    return []
            elif permission == "nuclear_files":
                if not user.nuclear_codes_access:
                    return []
            elif permission == "bio_files":
                if not user.biological_files_access:
                    return []
            return func(self, handler)

        return wrapper

    return decorator

class Server:
    def __init__(self, host, port, timeout):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.HOST = host
        self.PORT = port
        self.timeout = timeout
        self.socket.bind((self.HOST, self.PORT))
        self.socket.settimeout(1.0)
        self.client_handlers = list()
        self.lock = threading.Lock()
        self.running = True
        security.generate_master_key()
        try:
            with open("server_master.key", "rb") as f:
                self.master_key = f.read()
            self.master_fernet = Fernet(self.master_key)
            print("Server master key loaded successfully.")
        except FileNotFoundError:
            print("server_master.key not found.")



    def start(self):
        print(f"server {self.HOST}:{self.PORT} listening for connections")
        self.socket.listen(5)
        try:
            while self.running:
                try:
                    client_socket, addr = self.socket.accept()

                    if client_socket and addr and client_socket not in self.client_handlers:
                        client_handler = ClientHandler(client_socket, addr, self)
                        self.client_handlers.append(client_handler)
                        client_handler.start()
                except socket.timeout:
                    pass
        except KeyboardInterrupt:
            print("server stopped")
            self.running = False

        except Exception as e:
            print(f"server error: {e}")
        finally:
            self.shutdown()


    def shutdown(self):
        for handler in self.client_handlers:
            if handler.is_alive():
                exit_data = json.dumps({'type': 'server_closed'})
                try:
                    handler.client_socket.send(exit_data.encode("utf-8"))
                    handler.client_socket.close()
                    handler.db_conn.close()
                except Exception as e:
                    print(f"Exception: {e}")
                handler.stop()
                self.client_handlers.remove(handler)
        self.running = False


    def handle_login(self, handler: ClientHandler, username, input_password):
        response = {"type": "login_result","result":"incomplete"}
        cursor = handler.cursor
        try:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        except Exception as e:
            print(f"error: {e}")
        row = cursor.fetchone()
        if row:
            if len(row) == 0:
                print("row is empty")
            hashed_password = row[2]
            if bcrypt.checkpw(input_password.encode(), hashed_password):
                handler.login_user(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
                response = {
                    "type": "login_result",
                    "login_result": "success",
                    "user_id": str(row[0]),
                    "username": row[1],
                    "hashed_password": row[2].decode(),
                    "first_name": row[3],
                    "last_name": row[4],
                    "user_type": row[5],
                    "personnel_files_access": str(row[6]),
                    "nuclear_codes_access": str(row[7]),
                    "biological_files_access": str(row[8])
                }
            else:
                response = {
                    "type": "login_result",
                    "login_result": "incorrect password"
                }
        else:
            response = {
                "type": "login_result",
                "login_result": "incorrect username"
            }
        return response
    def handle_signup(self, handler: ClientHandler, data):
        response = {"type": "signup_result", "result": "incomplete"}
        cursor = handler.cursor
        try:
            cursor.execute('SELECT * FROM users WHERE username = ?', (data['username'],))
            username_row = cursor.fetchone()
            cursor.execute('SELECT * FROM users WHERE user_type = ?', ("secretary",))
            sec_row = cursor.fetchone()
            if username_row:
                response = {
                    "type": "signup_result",
                    "signup_result": "username_exists"
                }
            elif sec_row and data['user_type'] == "secretary":
                response = {
                    "type": "signup_result",
                    "signup_result": "secretary_exists"
                }
            elif data['user_type'] not in ("secretary", "agent"):
                response = {
                    "type": "signup_result",
                    "signup_result": "incorrect_user_type"
                }
            elif not (data['access_p']  in ("0", "1") and data['access_n']  in ("0", "1") and data['access_b']  in ("0", "1")):
                response = {
                    "type": "signup_result",
                    "signup_result": "incorrect_access"
                }
            else:
                hashed_password = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
                access_p = False if data['access_p'] == "0" else True
                access_n = False if data['access_n'] == "0" else True
                access_b = False if data['access_b'] == "0" else True
                cursor.execute('''
                    INSERT INTO users (username, hashed_password, first_name, last_name, user_type, personnel_files_access, nuclear_codes_access, biological_files_access) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data["username"], hashed_password, data["first_name"], data["last_name"], data["user_type"], access_p, access_n, access_b))
                handler.db_conn.commit()
                response = {
                    "type": "signup_result",
                    "signup_result": "success",
                    "user_id": str(username_row[0]),
                    "username": username_row[1],
                    "hashed_password": username_row[2].decode(),
                    "first_name": username_row[3],
                    "last_name": username_row[4],
                    "user_type": username_row[5],
                    "personnel_files_access": str(username_row[6]),
                    "nuclear_codes_access": str(username_row[7]),
                    "biological_files_access": str(username_row[8])
                }
        except Exception as e:
            print(f"error: {e}")
        return response

    def handle_file_lists(self, handler):
        response = {
            "type": "file_lists",
            "personnel_files": self.get_personnel_files(handler),
            "nuclear_files": self.get_nuclear_files(handler),
            "bio_files": self.get_bio_files(handler)
        }
        return response

    @requires_permission("personnel_files")
    def get_personnel_files(self, handler):
        files = [f for f in os.listdir("database/files/personnel_files")]
        return files

    @requires_permission("nuclear_files")
    def get_nuclear_files(self, handler):
        files = [f for f in os.listdir("database/files/nuclear_files")]
        return files

    @requires_permission("bio_files")
    def get_bio_files(self, handler):
        files = [f for f in os.listdir("database/files/bio_files")]
        return files

    def handle_update_files(self, handle,  data):
        for file in data['personnel_files']:
            try:
                fdata = bytes.fromhex(file['data'])
                encrypted_data = self.master_fernet.encrypt(fdata)
                filepath = f"database/files/personnel_files/{file['name']}"
                with open(filepath, "wb") as f:
                    f.write(encrypted_data)
            except Exception as e:
                print(f"error: {e}")
        for file in data['nuclear_files']:
            try:
                fdata = bytes.fromhex(file['data'])
                encrypted_data = self.master_fernet.encrypt(fdata)
                filepath = f"database/files/nuclear_files/{file['name']}"
                with open(filepath, "wb") as f:
                    f.write(encrypted_data)
            except Exception as e:
                print(f"error: {e}")
        for file in data['bio_files']:
            try:
                fdata = bytes.fromhex(file['data'])
                encrypted_data = self.master_fernet.encrypt(fdata)
                filepath = f"database/files/bio_files/{file['name']}"
                with open(filepath, "wb") as f:
                    f.write(encrypted_data)
            except Exception as e:
                print(f"error: {e}")


        









HOST = "127.0.0.1"
PORT = 9999
TIMEOUT = 100 #seconds
server = Server(host=HOST, port=PORT, timeout=TIMEOUT)
server.start()


# server_socket.bind((HOST, PORT))
#
# server_socket.listen(5)
# running = True
# while running:
#     client_socket, addr = server_socket.accept()
#     while True:
#         print('Got connection from: ', addr)
#         msg = client_socket.recv(1024).decode('utf-8')
#         if msg == 'exit server':
#             running = False
#             break
#         if msg == 'exit':
#             break
#         new_msg = capwords(msg)
#         client_socket.send(new_msg.encode('utf-8'))
#         print(f'message: "{new_msg}" sent to {addr}')
#     client_socket.close()