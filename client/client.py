import json
import socket

from main_window import MainWindow
from response_handling import ResponseHandler
from command_handling import CommandHandler

class Client:
    def __init__(self, host, port):
        super().__init__()
        self.HOST = host
        self.PORT = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(1.0)
        self.client_socket.connect((host, port))
        self.main_window: MainWindow

        self.cmd_handler = CommandHandler(self)
        self.rsp_handler = ResponseHandler(self.client_socket, self)
        self.rsp_handler.start()
        self.running = True
        self.data = {}
        self.logged_in = False

    def run(self):
        try:
            while self.running:
                command = input(">>> ").strip()
                if not self.running:
                    break




                msg = self.cmd_handler.handle_command(command)
                if msg:
                    print(f"sending message to server: {msg}")
                    self.client_socket.send(msg.encode())
                else:
                    print("incorrect command")

                if json.loads(msg)["type"] in ("exit_client", "exit_server"):
                    print("exiting")

                    self.running = False
        except Exception as e:
            print(e)


        self.client_socket.close()
        self.rsp_handler.running = False
        self.rsp_handler.join()



if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 9999
    client = Client(HOST, PORT)
    client.run()









# while True:
#     msg = input("sentence: ")
#     if msg.strip() == 'exit':
#         client_socket.send("exit".encode())
#         break
#     if msg.strip() == 'exit server':
#         client_socket.send("exit server".encode())
#         break
#     client_socket.send(msg.encode())
#     new_msg = client_socket.recv(1024).decode("utf-8")
#     print(f"capitalized message: {new_msg}")

