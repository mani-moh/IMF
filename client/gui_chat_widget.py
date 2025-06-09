
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
                               QTextBrowser, QTextEdit, QPushButton, QInputDialog,
                               QListWidgetItem, QDialog, QLabel, QLineEdit)
from PySide6.QtCore import Qt
import json

from gui_chat_list_widget import ChatListWidget


class ChatWidget(QWidget):
    def __init__(self, client, parent=None):
        super(ChatWidget, self).__init__(parent)
        self.client = client
        self.parent = parent
        self.chats = {
            "dm": [],
            "group": []
        }
        self.current_chat = {
            "type": None,
            "id": None,
            "name": None,
        }  # To store the username of the current chat
        self.current_chat_item: ChatListWidget

        # --- Main Layout ---
        self.chat_layout = QHBoxLayout()
        self.setLayout(self.chat_layout)

        # --- Left Panel (Conversations List) ---
        left_panel_layout = QVBoxLayout()
        self.convo_list = QListWidget()
        self.convo_list.itemClicked.connect(self.on_convo_selected)
        left_panel_layout.addWidget(self.convo_list)

        self.new_chat_button = QPushButton("New Chat")
        self.new_chat_button.clicked.connect(self.start_new_chat)
        left_panel_layout.addWidget(self.new_chat_button)

        self.chat_layout.addLayout(left_panel_layout, stretch=1)

        # --- Right Panel (Chat Area) ---
        self.chat_area = QWidget()
        self.chat_area_layout = QVBoxLayout(self.chat_area)
        self.chat_layout.addWidget(self.chat_area, stretch=3)

        self.chat_display = QTextBrowser()
        self.chat_display.setReadOnly(True)
        self.chat_area_layout.addWidget(self.chat_display, stretch=20)

        chatting_widget = QWidget()
        chatting_widget.setMaximumHeight(100)
        self.chat_area_layout.addWidget(chatting_widget, stretch=1)
        chatting_layout = QHBoxLayout(chatting_widget)

        self.message_input = QTextEdit()

        chatting_layout.addWidget(self.message_input, stretch=10)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        chatting_layout.addWidget(self.send_button, stretch=1)

        # Hide chat area until a conversation is selected
        self.chat_area.hide()

    def start_new_chat(self):
        """For now, this just serves as a placeholder for starting chats or groups."""
        # A more advanced implementation would show a list of users to chat with.
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("New Chat")
        self.dialog.setLayout(QVBoxLayout())
        label = QLabel("username:")
        self.dialog.layout().addWidget(label)
        self.new_chat_input = QLineEdit()
        self.dialog.layout().addWidget(self.new_chat_input)
        self.create_new_chat_button = QPushButton("Create New Chat")
        self.create_new_chat_button.clicked.connect(self.create_new_chat)
        self.dialog.layout().addWidget(self.create_new_chat_button)
        self.dialog.exec()


    def create_new_chat(self):
        username = self.new_chat_input.text()
        if username:
            req = {
                "type": "create_chat",
                "username": username
            }
            self.client.client_socket.send(json.dumps(req).encode())
            self.dialog.close()

    def got_create_chat(self,response):
        if response["status"] == 'success':
            self.add_chat_to_list(response["username"], "dm", response["id"])



    def on_convo_selected(self, item):
        """Loads the conversation for the selected user."""
        self.current_chat["type"] = item.chat_type
        self.current_chat["id"] = item.chat_id
        self.current_chat["name"] = item.chat_name
        self.current_chat_item = item
        self.chat_display.clear()
        self.chat_display.append(f"<b>--- Chat with {self.current_chat["name"]} ---</b>")
        self.chat_area.show()
        self.request_chat_history(self.current_chat["type"], self.current_chat["id"])
        # In a full implementation, you would request chat history from the server here.

    def request_chat_history(self, chat_type, chat_id):
        print(f"chat type: {chat_type}")
        req = {
            "type": "request_chat_history",
            "chat_type": chat_type,
            "chat_id": chat_id,
        }
        self.client.client_socket.send(json.dumps(req).encode())
    def show_chat_history(self, chat_type, chat_id, messages):
        if self.current_chat["type"] == chat_type and self.current_chat["id"] == chat_id:
            for message in messages:
                sender = message["sender_name"]
                if sender == self.client.data["username"]:
                    sender = "You"
                self.chat_display.append(f"<font color='yellow'><b>{sender}: </b></font>{message["content"]}")

    def update_chat_list(self):
        req = {
            "type": "update_chat_list",
        }
        self.client.client_socket.send(json.dumps(req).encode())
    def got_update_chat_list(self, response):
        for chat in response["chats"]:
            self.add_chat_to_list(chat["name"], chat["chat_type"], chat["id"])

    def send_message(self):
        """Sends a message to the currently selected chat partner."""
        message_text = self.message_input.toPlainText().strip()
        if not message_text or not self.current_chat:
            return

        req_json = {
            'type': 'send_chat_message',
            'recipient': self.current_chat,
            'content': message_text
        }

        try:
            req = json.dumps(req_json)
            self.client.client_socket.send(req.encode())
            # Display sent message immediately
            self.chat_display.append(f"<font color='cyan'><b>You:</b></font> {message_text}")
            self.message_input.clear()
        except Exception as e:
            print(f"Error sending message: {e}")

    def add_chat_to_list(self, chat_name, chat_type, chat_id):
        """Adds a user to the conversation list if not already present."""
        if chat_id not in self.chats[chat_type]:
            self.convo_list.addItem(ChatListWidget(chat_name, chat_type, chat_id))

    def incoming_message(self, rsp):
        sender = rsp["sender"]
        sender_id = sender["id"]
        sender_name = sender["name"]
        content = rsp["content"]
        if rsp["chat_type"] == 'group':
            if self.current_chat["id"] == rsp["group_id"]:
                self.chat_display.append(f"<font color='yellow'><b>{sender_name}</b></font>: {content}")
        else:
            if self.current_chat["id"] == sender_id:
                self.chat_display.append(f"<font color='yellow'><b>{sender_name}</b></font>: {content}")

    def remove_user_from_list(self, username):
        """Removes a user from the conversation list."""
        items = self.convo_list.findItems(username, Qt.MatchFlag.MatchExactly)
        for item in items:
            self.convo_list.takeItem(self.convo_list.row(item))

    def display_incoming_message(self, sender, content):
        """Displays a message received from another user."""
        # If the message is from the current chat partner, display it
        if sender == self.current_chat:
            self.chat_display.append(f"<font color='yellow'><b>{sender}:</b></font> {content}")
        else:
            # Otherwise, you could show a notification
            print(f"New message from {sender} (not in current view)")