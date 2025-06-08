from PySide6.QtWidgets import QMainWindow, QApplication, QStackedWidget, QWidget, QVBoxLayout
import json

from gui_stacked_widget import StackedWidget
from gui_tabs_widget import TabsWidget


class MainWindow(QMainWindow):
    min_x = 600
    min_y = 400


    def __init__(self, client):
        super().__init__()
        #attributes
        self.client = client

        #sets minimum window size
        self.setMinimumSize(self.min_x, self.min_y)

        #sets the starting size
        screen = QApplication.primaryScreen()
        if screen:
            geometry_qrect = screen.availableGeometry()

            width = max(geometry_qrect.width() // 2, self.min_x)
            height = max(geometry_qrect.height() // 2, self.min_y)
            left = (geometry_qrect.width() - width) // 2
            top = (geometry_qrect.height() - height) // 2

            self.setGeometry(left, top, width, height)

        #sets window title
        self.setWindowTitle('IMF')

        #sets the central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.central_widget.setLayout(QVBoxLayout())

        self.stacked_widget = StackedWidget(self.client, self.central_widget)
        self.tabs_widget = TabsWidget(self.stacked_widget, self.client, self.central_widget)
        self.central_widget.layout().addWidget(self.tabs_widget)
        self.central_widget.layout().addWidget(self.stacked_widget)

    def closeEvent(self, event):
        msg = json.dumps({'type': 'exit_client'})
        self.client.client_socket.send(msg.encode())
        self.client.running = False
        self.delete_files("files/personnel_files")
        self.delete_files("files/nuclear_files")
        self.delete_files("files/bio_files")
        super().closeEvent(event)


    def delete_files(self, directory):
        import os

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")