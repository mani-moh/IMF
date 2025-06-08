import socket
import threading
import os
import json
import logging
from datetime import datetime

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)


class FileServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # Store connections as {conn: username}
        self.next_user_id = 1
        self.files_dir = 'server/files'
        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir)

    def start(self):
        """Binds the server to the address and starts listening for connections."""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            logging.info(f"Server started on {self.host}:{self.port} and listening...")
            while True:
                conn, addr = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
        except OSError as e:
            logging.error(f"Failed to start server: {e}")

    def handle_client(self, conn, addr):
        """Handles a new client connection."""
        username = f"User-{self.next_user_id}"
        self.next_user_id += 1
        self.clients[conn] = username
        logging.info(f"New connection from {addr} as {username}")

        try:
            # Announce new user to all other clients
            self.broadcast_system_message(f"'{username}' has joined the chat.", conn)
            # Send the new user their assigned username
            conn.sendall(json.dumps({'type': 'assign_username', 'username': username}).encode())
            # Send the initial file list
            self.send_file_list(conn)

            while True:
                data_bytes = conn.recv(1024)
                if not data_bytes:
                    break  # Client disconnected

                # Handle potentially concatenated JSON messages
                for data in self.decode_json_stream(data_bytes):
                    self.process_message(data, conn)

        except (ConnectionResetError, BrokenPipeError):
            logging.warning(f"Connection lost with {username} ({addr})")
        except Exception as e:
            logging.error(f"An error occurred with client {username}: {e}")
        finally:
            # Cleanup after client disconnection
            if conn in self.clients:
                username = self.clients.pop(conn)
                conn.close()
                self.broadcast_system_message(f"'{username}' has left the chat.")
                logging.info(f"Connection with {username} ({addr}) closed.")

    def decode_json_stream(self, stream_bytes):
        """Decodes a stream of bytes that may contain multiple JSON objects."""
        stream = stream_bytes.decode('utf-8')
        # This handles cases where multiple JSON messages are received in one batch
        # by splitting based on the structure of `}{`
        stream = stream.replace('}{', '}\n{')
        for json_str in stream.split('\n'):
            if json_str.strip():
                try:
                    yield json.loads(json_str)
                except json.JSONDecodeError:
                    logging.warning(f"Could not decode JSON: {json_str}")

    def process_message(self, message, conn):
        """Processes a single JSON message from a client."""
        msg_type = message.get('type')
        username = self.clients.get(conn, "Unknown")

        if msg_type == 'list_files':
            logging.info(f"Request for file list from {username}.")
            self.send_file_list(conn)
        elif msg_type == 'download_file':
            filename = message.get('filename')
            logging.info(f"Request to download '{filename}' from {username}.")
            self.send_file(conn, filename)
        elif msg_type == 'chat_message':
            text = message.get('text')
            logging.info(f"Chat from {username}: {text}")
            self.broadcast_chat_message(text, username)

    def broadcast_chat_message(self, text, sender_username):
        """Broadcasts a chat message to all clients."""
        message = {'type': 'chat_message', 'username': sender_username, 'text': text}
        self.broadcast(message)

    def broadcast_system_message(self, text, except_conn=None):
        """Broadcasts a system message (like connect/disconnect) to all clients."""
        message = {'type': 'system_message', 'text': text}
        self.broadcast(message, except_conn)

    def broadcast(self, message, except_conn=None):
        """Helper function to send a message to all connected clients."""
        message_json = json.dumps(message)
        for client_conn in list(self.clients.keys()):
            if client_conn != except_conn:
                try:
                    client_conn.sendall(message_json.encode())
                except (ConnectionResetError, BrokenPipeError):
                    # The handle_client loop will manage cleanup of this dead connection
                    logging.warning("Failed to send message to a client, connection may be closed.")

    def send_file_list(self, conn):
        """Sends the list of available files to a specific client."""
        try:
            files = os.listdir(self.files_dir)
            message = {'type': 'file_list', 'files': files}
            conn.sendall(json.dumps(message).encode())
        except Exception as e:
            logging.error(f"Error sending file list: {e}")

    def send_file(self, conn, filename):
        """Sends a requested file to a specific client."""
        filepath = os.path.join(self.files_dir, filename)
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                # Using hex encoding is simple but can be inefficient for large files
                message = {'type': 'file_data', 'filename': filename, 'data': file_data.hex()}
                conn.sendall(json.dumps(message).encode())
            except Exception as e:
                logging.error(f"Error sending file '{filename}': {e}")
        else:
            # Inform client that the file doesn't exist
            message = {'type': 'error', 'text': f"File '{filename}' not found on server."}
            conn.sendall(json.dumps(message).encode())
            logging.warning(f"File '{filename}' requested but not found.")


if __name__ == "__main__":
    # Create some dummy files for testing if they don't exist
    files_to_create = {'test1.txt': 'This is a test file.', 'document.pdf': 'PDF content placeholder'}
    if not os.path.exists('server/files'):
        os.makedirs('server/files')
    for name, content in files_to_create.items():
        path = os.path.join('server/files', name)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(content)
            logging.info(f"Created dummy file: {name}")

    server = FileServer()
    server.start()
