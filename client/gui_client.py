import threading

from PySide6.QtWidgets import QApplication
import sys
from client import Client
from main_window import MainWindow

HOST = '127.0.0.1'
PORT = 9999
client = Client(HOST, PORT)
# cli_thread = threading.Thread(target=client.run)
# cli_thread.start()
app = QApplication(sys.argv)
main_window = MainWindow(client)
main_window.show()
client.main_window = main_window
try:
    app.exec()
except KeyboardInterrupt:
    main_window.close()
except Exception as e:
    print(e)