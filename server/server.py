import bcrypt
from cryptography.fernet import Fernet
import socket
import threading
from client_handling import ClientHandler
import json, os
import security
import database.database as database


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
        database.init_db()
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
                online_announcement = {"type": "user_online", "username": row[1]}

                # Send list of online users to the new client
                online_users = [h.user.username for h in self.client_handlers if h.user.username and h is not handler]
                user_list_msg = {"type": "online_users_list", "users": online_users}
                handler.client_socket.send(json.dumps(user_list_msg).encode())
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

    def broadcast(self, message, source_handler=None):
        """Sends a message to all connected clients, optionally excluding the source."""
        for handler in self.client_handlers:
            if handler is not source_handler and handler.user.id:
                try:
                    handler.client_socket.sendall(json.dumps(message).encode())
                except Exception as e:
                    print(f"Error broadcasting message: {e}")

    def handle_send_chat_message(self, handler, data):
        """Handles sending a private chat message to another user."""
        recipient = data.get('recipient')
        content = data.get('content')
        sender = handler.user

        if recipient['type'] == 'dm':
            recipient_handler = None
            for h in self.client_handlers:
                if h.user.id == recipient['id']:
                    recipient_handler = h
                    break

            if recipient_handler:
                # Forward the message to the recipient
                message = {
                    "type": "incoming_chat_message",
                    "chat_type": "dm",
                    "sender": {"id": sender.id, "name": sender.username},
                    "content": content
                }
                print(type(recipient_handler.client_socket))
                try:
                    recipient_handler.client_socket.sendall(json.dumps(message).encode())
                except Exception as e:
                    print(f"Error here message: {e}")
            else:
                # Optional: Handle offline users (e.g., store message in DB for later)
                print(f"User {recipient['username']} is not online.")
            cursor = handler.cursor
            cursor.execute('''
            INSERT INTO messages (sender_id, recipient_id, content) VALUES (?, ?, ?)
            ''', (sender.id, recipient['id'], content))
            handler.db_conn.commit()
        elif recipient['type'] == 'group':
            group = recipient
            recipients = self.get_recipients_by_groupid(recipient['id'], handler)
            for recipient in recipients:
                self.forward_to_rec(handler, recipient, data)
            cursor = handler.cursor
            cursor.execute('''
                        INSERT INTO messages (sender_id, group_id, content) VALUES (?, ?, ?)
                        ''', (sender.id, group['id'], content))
            handler.db_conn.commit()
    def forward_to_rec(self, handler, recipient, data):
        rec_data = data.get('recipient')
        content = data.get('content')
        sender = handler.user
        recipient_handler = None
        for h in self.client_handlers:
            if h.user.id == recipient['user_id']:
                recipient_handler = h
                break

        if recipient_handler:
            # Forward the message to the recipient
            message = {
                "type": "incoming_chat_message",
                "chat_type": "group",
                "group_id": rec_data['id'],
                "sender": {"id": sender.id, "name": sender.username},
                "content": content
            }
            recipient_handler.client_socket.sendall(json.dumps(message).encode())


    def get_recipients_by_groupid(self, groupid, handler):
        recs = []
        cursor = handler.cursor
        cursor.execute('''
        SELECT user_id WHERE groupid = ?
        ''', (groupid,))
        rows = cursor.fetchall()
        for row in rows:
            recs.append({'user_id': row[0], 'username': self.get_username_by_id(handler, row[0])})
        return recs

    def handle_request_chat_history(self, handler, data):
        cursor = handler.cursor
        chat_type = data['chat_type']
        chat_id = int(data['chat_id'])
        name_by_id = {}
        messages = []
        if chat_type == "dm":
            cursor.execute('''
            SELECT * FROM messages WHERE (sender_id = ? AND recipient_id = ?) OR (sender_id = ? AND recipient_id = ?);
            ''', (chat_id, handler.user.id, handler.user.id, chat_id))
            rows = cursor.fetchall()

            for row in rows:
                print(row)
                messages.append({"sender_id": int(row[1]), "sender_name": self.get_username_by_id(handler, int(row[1]), name_by_id), "content": row[4], "date": row[5]})
            response = {
                'type': 'chat_history',
                'chat_type': chat_type,
                'chat_id': chat_id,
                'messages': messages
            }
            return response
        elif chat_type == "group":
            cursor.execute('''
                        SELECT * FROM messages WHERE groupid = ?;
                        ''', (chat_id,))
            rows = cursor.fetchall()
            for row in rows:
                messages.append({"sender_id": int(row[1]), "sender_name": self.get_username_by_id(handler, int(row[1]), name_by_id), "content": row[4], "date": row[5]})
            response = {
                'type': 'chat_history',
                'chat_type': chat_type,
                'chat_id': chat_id,
                'messages': messages
            }
            return response


    def get_username_by_id(self, handler, user_id, name_by_id = None):

        if name_by_id:
            if user_id in name_by_id:
                return name_by_id[user_id]
            else:
                cursor = handler.cursor
                cursor.execute('''
                SELECT username FROM users WHERE id = ?;
                ''', (user_id,))
                row = cursor.fetchone()
                if row:
                    username = cursor.fetchone()[0]
                    name_by_id[user_id] = username
                    return username
                else:
                    return None
        else:
            cursor = handler.cursor
            cursor.execute('''
                            SELECT username FROM users WHERE id = ?;
                            ''', (user_id,))
            row = cursor.fetchone()
            if row:
                username = row[0]
                return username
            else:
                return None

    def handle_create_chat(self, handler, data):
        cursor = handler.cursor
        username = data['username']
        cursor.execute('''
        SELECT id FROM users WHERE username = ?;
        ''', (username,))
        row = cursor.fetchone()
        if row:
            response = {
                "type": "create_chat",
                "status": "success",
                "id": row[0],
                "username": username
            }
        else:
            response = {
                "type": "create_chat",
                "status": "fail",
            }
        return response

    def handle_update_chat_list(self, handler, data):
        cursor = handler.cursor
        user_id = handler.user.id
        response = {
            "type": "update_chat_list",
            "chats": []
        }
        dm_ids = set()
        cursor.execute('''
        SELECT * FROM messages WHERE sender_id = ? OR recipient_id = ?;
        ''', (user_id ,user_id))
        rows = cursor.fetchall()

        for row in rows:
            if row[3] is None:
                if row[1] == user_id:
                    dm_ids.add(row[2])
                elif row[2] == user_id:
                    dm_ids.add(row[1])
        for dm_id in dm_ids:
            response['chats'].append({"chat_type": "dm" , "id": dm_id, "name": self.get_username_by_id(handler, dm_id)})

        cursor.execute('''
        SELECT gm.group_id, gm.user_id, g.group_name
        FROM groups g
        JOIN group_members gm ON gm.group_id = g.group_id
        WHERE user_id = ?;
        ''', (user_id,))
        rows = cursor.fetchall()
        for row in rows:
            response['chats'].append({"chat_type": "group", "id": row[0], "name": row[2]})
        return response

    def handle_delete_file(self, handler, data):
        filepath = os.path.join("database", "files", data['file_type'], data['file_name'])

        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    print(f"Deleted file: {filepath}")
            except Exception as e:
                print(f"Failed to delete {filepath}. Reason: {e}")
            # try:
            #     with open(filepath, "rb") as file:
            #         file_data = file.read()  # Read in chunks
            #     file_data_dec = self.server_instance.master_fernet.decrypt(file_data)
            #     response_data = {'type': 'file_data', 'file_name': data['file_name'], 'file_type': data['file_type'],
            #                      "status": "success", 'data': file_data_dec.hex()}
            #     print("sent file")
            # except Exception as e:
            #     print(f"Exception on sendfile: {str(e)}")
        else:
            print("path/file not exist")






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