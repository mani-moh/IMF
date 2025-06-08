from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QTextBrowser, QTextEdit, QPushButton
from PySide6.QtCore import Qt

class ChatWidget(QWidget):
    def __init__(self, client, parent=None):
        super(ChatWidget, self).__init__(parent)
        self.client = client
        self.parent = parent
        self.chat_layout = QHBoxLayout()
        self.setLayout(self.chat_layout)

        self.convo_list = QListWidget()
        self.chat_layout.addWidget(self.convo_list, stretch=10)

        self.chat_area = QWidget()
        self.chat_area_layout = QVBoxLayout(self.chat_area)
        self.chat_layout.addWidget(self.chat_area, stretch=30)

        self.chat_display = QTextBrowser()
        self.chat_display.setReadOnly(True)
        self.chat_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.chat_area_layout.addWidget(self.chat_display, stretch=10)

        self.chatting_widget = QWidget()
        self.chat_area_layout.addWidget(self.chatting_widget, stretch=1)
        self.chatting_layout = QHBoxLayout()
        self.chatting_widget.setLayout(self.chatting_layout)

        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.chatting_layout.addWidget(self.message_input, stretch=10)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.chatting_layout.addWidget(self.send_button, stretch=1)

    def send_message(self):
        pass