import sys
import socket
import threading
import json
import os
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                               QListWidget, QTextEdit, QLineEdit, QLabel, QHBoxLayout,
                               QMessageBox, QListWidgetItem, QStatusBar, QMainWindow)
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtGui import QFont


class Communicate(QObject):
    """Signal handler to safely update the UI from other threads."""
    msg_signal = Signal(dict)


class FileClient(QMainWindow):
    def __init__(self, host='127.0.0.1', port=65432):
        super().__init__()
        self.host = host
        self.port = port
        self.client_socket = None
        self.username = "Connecting..."
        self.files_dir = 'client/files'
        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir)

        # Communication signal for thread-safe UI updates
        self.comm = Communicate()
        self.comm.msg_signal.connect(self.handle_message)

        self.init_ui()
        self.connect_to_server()

    def init_ui(self):
        """Initializes the user interface."""
        self.setWindowTitle('File Sharer and Chat')
        self.setGeometry(100, 100, 500, 600)

        # --- Central Widget and Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- File List Section ---
        file_layout = QHBoxLayout()
        self.file_list_label = QLabel('Server Files:')
        self.file_list_label.setFont(QFont("Arial", 10, QFont.Bold))

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.request_file_list)

        file_layout.addWidget(self.file_list_label)
        file_layout.addStretch()
        file_layout.addWidget(refresh_button)

        main_layout.addLayout(file_layout)

        self.file_list_widget = QListWidget()
        main_layout.addWidget(self.file_list_widget, 2)  # Give more stretch factor

        # --- Chat Section ---
        self.chat_label = QLabel('Chat:')
        self.chat_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(self.chat_label)

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        main_layout.addWidget(self.chat_box, 3)  # Give more stretch factor

        # --- Message Input Section ---
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message...")
        self.chat_input.returnPressed.connect(self.send_chat_message)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_chat_message)

        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(self.send_button)
        main_layout.addLayout(chat_input_layout)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Disconnected")

    def connect_to_server(self):
        """Establishes connection to the server and starts the listening thread."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.status_bar.showMessage(f"Connected to {self.host}:{self.port}")

            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
        except ConnectionRefusedError:
            self.show_error_dialog("Connection Failed", "Could not connect to the server. Is it running?")
            QApplication.instance().quit()

    def receive_messages(self):
        """Listens for incoming messages from the server."""
        buffer = ""
        while True:
            try:
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data:
                    self.comm.msg_signal.emit({'type': 'system_error', 'text': 'Connection to server lost.'})
                    break

                buffer += data
                # Process multiple JSON objects if they are received together
                while '}{' in buffer:
                    end_index = buffer.find('}{') + 1
                    message_str = buffer[:end_index]
                    buffer = buffer[end_index:]
                    try:
                        message = json.loads(message_str)
                        self.comm.msg_signal.emit(message)
                    except json.JSONDecodeError:
                        pass  # Wait for more data

                # Process the last/remaining message
                if buffer:
                    try:
                        message = json.loads(buffer)
                        self.comm.msg_signal.emit(message)
                        buffer = ""  # Clear buffer after successful parse
                    except json.JSONDecodeError:
                        pass  # Incomplete message, wait for more data

            except (ConnectionResetError, OSError):
                self.comm.msg_signal.emit({'type': 'system_error', 'text': 'Connection to server lost.'})
                break
            except Exception as e:
                self.comm.msg_signal.emit({'type': 'system_error', 'text': f'An error occurred: {e}'})
                break

    def handle_message(self, message):
        """Processes messages received from the server and updates the UI."""
        msg_type = message.get('type')

        if msg_type == 'assign_username':
            self.username = message.get('username', 'User')
            self.setWindowTitle(f"File Sharer and Chat - [{self.username}]")
        elif msg_type == 'file_list':
            self.update_file_list(message.get('files', []))
        elif msg_type == 'file_data':
            self.save_file(message.get('filename'), message.get('data'))
        elif msg_type == 'chat_message':
            self.append_chat_message(f"<{message.get('username')}> {message.get('text')}")
        elif msg_type == 'system_message':
            self.append_system_message(message.get('text'))
        elif msg_type == 'error':
            self.show_error_dialog("Server Error", message.get('text'))
        elif msg_type == 'system_error':
            self.show_error_dialog("Connection Error", message.get('text'))
            self.status_bar.showMessage("Disconnected")
            if self.client_socket:
                self.client_socket.close()

    def update_file_list(self, files):
        """Clears and repopulates the file list widget."""
        self.file_list_widget.clear()
        if not files:
            self.file_list_widget.addItem("No files on server.")
            return

        for filename in files:
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(5, 5, 5, 5)

            label = QLabel(filename)
            download_button = QPushButton('Download')
            download_button.setFixedWidth(80)
            # Use a lambda to capture the current filename for the click event
            download_button.clicked.connect(lambda ch, f=filename: self.download_file(f))

            item_layout.addWidget(label)
            item_layout.addStretch()
            item_layout.addWidget(download_button)
            item_widget.setLayout(item_layout)

            list_item = QListWidgetItem(self.file_list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.file_list_widget.addItem(list_item)
            self.file_list_widget.setItemWidget(list_item, item_widget)

    def download_file(self, filename):
        """Sends a file download request to the server."""
        if not self.client_socket: return
        self.status_bar.showMessage(f"Downloading '{filename}'...", 3000)
        message = {'type': 'download_file', 'filename': filename}
        try:
            self.client_socket.sendall(json.dumps(message).encode())
        except (ConnectionResetError, BrokenPipeError):
            self.comm.msg_signal.emit({'type': 'system_error', 'text': 'Connection to server lost.'})

    def save_file(self, filename, hex_data):
        """Saves a downloaded file to the local directory."""
        if not filename or not hex_data: return
        filepath = os.path.join(self.files_dir, filename)
        try:
            with open(filepath, 'wb') as f:
                f.write(bytes.fromhex(hex_data))
            self.append_system_message(f"File '{filename}' downloaded to '{self.files_dir}'.")
            self.status_bar.showMessage(f"Download of '{filename}' complete.", 5000)
        except (ValueError, TypeError) as e:
            self.show_error_dialog("Download Error", f"Failed to decode or save file '{filename}': {e}")

    def request_file_list(self):
        """Sends a request to the server to get the latest file list."""
        if not self.client_socket: return
        message = {'type': 'list_files'}
        try:
            self.client_socket.sendall(json.dumps(message).encode())
            self.status_bar.showMessage("Refreshing file list...", 2000)
        except (ConnectionResetError, BrokenPipeError):
            self.comm.msg_signal.emit({'type': 'system_error', 'text': 'Connection to server lost.'})

    def send_chat_message(self):
        """Sends a chat message to the server."""
        text = self.chat_input.text().strip()
        if text and self.client_socket:
            message = {'type': 'chat_message', 'text': text}
            try:
                self.client_socket.sendall(json.dumps(message).encode())
                self.append_chat_message(f"<You> {text}")
                self.chat_input.clear()
            except (ConnectionResetError, BrokenPipeError):
                self.comm.msg_signal.emit({'type': 'system_error', 'text': 'Connection to server lost.'})

    def append_chat_message(self, text):
        """Adds a standard chat message to the chat box."""
        self.chat_box.append(text)

    def append_system_message(self, text):
        """Adds an italicized system message to the chat box."""
        self.chat_box.append(f"<i>[System] {text}</i>")

    def show_error_dialog(self, title, text):
        """Displays a modal error message box."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        """Ensure socket is closed when the window is shut."""
        if self.client_socket:
            self.client_socket.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = FileClient()
    client.show()
    sys.exit(app.exec())
