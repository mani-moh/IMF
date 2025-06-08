# server.py
import os
import socket
from threading import Thread
from time import sleep

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5001
BUFFER_SIZE = 4096
FILES_DIR = 'server/files'


def handle_client_connection(client_socket):
    try:
        # Receive the requested filename
        filename = client_socket.recv(BUFFER_SIZE).decode()
        filepath = os.path.join(FILES_DIR, filename)

        if not os.path.exists(filepath):
            client_socket.send(b'File not found')
            return

        # Send the file
        with open(filepath, 'rb') as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()


def start_server():
    # Create server directory if it doesn't exist
    if not os.path.exists(FILES_DIR):
        os.makedirs(FILES_DIR)

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Accepted connection from {address}")
            client_handler = Thread(
                target=handle_client_connection,
                args=(client_socket,)
            )
            client_handler.start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()