from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
import json, socket
from cryptography.fernet import Fernet

class SecFileNameWidget(QWidget):
    def __init__(self, client, file_type, filename, mfile, parent=None):
        super().__init__(parent)
        self.mfile = mfile
        self.client = client
        self.file_type = file_type
        self.filename = filename
        self.setMinimumHeight(100)
        self.file_layout = QHBoxLayout()
        self.setLayout(self.file_layout)
        self.file_layout.setContentsMargins(0, 0, 0, 0)
        self.file_layout.setSpacing(0)

        self.label = QLabel(filename)

        self.button = QPushButton('delete')

        self.file_layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignTop)
        self.file_layout.addWidget(self.button, 0, Qt.AlignmentFlag.AlignTop)

        self.button.clicked.connect(self.delete_file)

    def delete_file(self):
        req_json = {
            'type': 'delete_file',
            'file_type': self.file_type,
            'file_name': self.filename
        }

        try:
            req = json.dumps(req_json)
            self.client.client_socket.send(req.encode())
        except Exception as e:
            print("Error: " + str(e))




