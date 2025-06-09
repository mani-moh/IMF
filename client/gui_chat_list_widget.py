from PySide6.QtWidgets import QWidget, QListWidgetItem


class ChatListWidget(QListWidgetItem):
    def __init__(self, chat_name, chat_type, chat_id):
        super().__init__(chat_name)
        self.chat_name = chat_name
        self.chat_type = chat_type
        self.chat_id = chat_id