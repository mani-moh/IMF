from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
import json, socket
from cryptography.fernet import Fernet

class FileNameWidget(QWidget):
    def __init__(self, client, file_type, filename, parent=None):
        super().__init__(parent)
        self.client = client
        self.file_type = file_type
        self.filename = filename
        self.file_layout = QHBoxLayout()
        self.setLayout(self.file_layout)

        self.label = QLabel(filename)
        self.file_layout.addWidget(self.label)

        self.button = QPushButton('download')
        self.file_layout.addWidget(self.button)
        self.button.clicked.connect(self.download_file)

    def download_file(self):
        req_json = {
            'type': 'download_file',
            'file_type': self.file_type,
            'file_name': self.filename
        }

        try:
            req = json.dumps(req_json)
            self.client.client_socket.send(req.encode())
        except Exception as e:
            print("Error: " + str(e))




        try:
            rsp = self.client.client_socket.recv(1024).decode()
            rsp_json = json.loads(rsp)
            if rsp_json['type'] == 'file_data' and rsp_json['file_name'] == self.filename and rsp_json['status'] == 'success':
                with open(f"files/{self.file_type}/{self.filename}", 'wb') as f:
                    data = bytes.fromhex(rsp_json['data'])
                    f.write(data)
        except Exception as e:
            print("Error while downloading file: " + str(e))