# client.py
import os
import socket
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QListWidget, QPushButton, QListWidgetItem, QHBoxLayout,
    QLabel, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal

SERVER_HOST = 'localhost'
SERVER_PORT = 5001
BUFFER_SIZE = 4096
CLIENT_FILES_DIR = 'client/files'


class FileDownloader(QThread):
    update_progress = Signal(str, int)  # filename, progress
    download_complete = Signal(str, bool)  # filename, success

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def run(self):
        try:
            # Create client directory if it doesn't exist
            if not os.path.exists(CLIENT_FILES_DIR):
                os.makedirs(CLIENT_FILES_DIR)

            # Connect to server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, SERVER_PORT))

            # Send the filename to download
            client_socket.send(self.filename.encode())

            # Receive the file
            filepath = os.path.join(CLIENT_FILES_DIR, self.filename)
            total_bytes = 0

            with open(filepath, 'wb') as f:
                while True:
                    bytes_read = client_socket.recv(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    total_bytes += len(bytes_read)
                    self.update_progress.emit(self.filename, total_bytes)

            self.download_complete.emit(self.filename, True)
        except Exception as e:
            print(f"Download error: {e}")
            self.download_complete.emit(self.filename, False)
        finally:
            client_socket.close()


class FileListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Download Client")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.title_label = QLabel("Available Files on Server")
        self.layout.addWidget(self.title_label)

        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)

        self.refresh_button = QPushButton("Refresh File List")
        self.refresh_button.clicked.connect(self.get_file_list)
        self.layout.addWidget(self.refresh_button)

        # Dictionary to track download progress
        self.download_progress = {}

        # Get initial file list
        self.get_file_list()

    def get_file_list(self):
        try:
            # Connect to server to get file list
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            client_socket.send(b'LIST_FILES')

            # Receive the file list
            file_list_data = client_socket.recv(BUFFER_SIZE).decode()
            files = file_list_data.split('\n') if file_list_data else []

            self.file_list.clear()

            for filename in files:
                if not filename:
                    continue

                item = QListWidgetItem()
                widget = QWidget()
                layout = QHBoxLayout()

                label = QLabel(filename)
                layout.addWidget(label, stretch=1)

                download_btn = QPushButton("Download")
                download_btn.clicked.connect(lambda _, f=filename: self.download_file(f))
                layout.addWidget(download_btn)

                progress_label = QLabel("")
                layout.addWidget(progress_label)
                self.download_progress[filename] = progress_label

                widget.setLayout(layout)
                item.setSizeHint(widget.sizeHint())

                self.file_list.addItem(item)
                self.file_list.setItemWidget(item, widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not connect to server: {e}")
        finally:
            client_socket.close()

    def download_file(self, filename):
        if filename in self.download_progress:
            self.download_progress[filename].setText("Downloading...")

        self.downloader = FileDownloader(filename)
        self.downloader.update_progress.connect(self.update_progress)
        self.downloader.download_complete.connect(self.download_finished)
        self.downloader.start()

    def update_progress(self, filename, bytes_received):
        if filename in self.download_progress:
            self.download_progress[filename].setText(f"Downloaded: {bytes_received} bytes")

    def download_finished(self, filename, success):
        if filename in self.download_progress:
            if success:
                self.download_progress[filename].setText("Download complete!")
                QMessageBox.information(self, "Success", f"File '{filename}' downloaded successfully")
            else:
                self.download_progress[filename].setText("Download failed")
                QMessageBox.warning(self, "Error", f"Failed to download '{filename}'")


if __name__ == "__main__":
    app = QApplication([])
    window = FileListWindow()
    window.show()
    app.exec()