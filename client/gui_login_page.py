import socket

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QStackedWidget
import json

from gui_viewfile_widget import ViewFileWidget


class LoginPage(QWidget):
    def __init__(self, client, start_page, parent=None):
        super().__init__(parent)
        self.client = client
        self.parent = parent
        self.start_page = start_page
        self.login_layout = QVBoxLayout()
        self.setLayout(self.login_layout)


        self.input_username = QLineEdit(self)
        self.input_username.setPlaceholderText("Username")
        self.input_username.setMaxLength(50)
        self.input_username.setMaximumWidth(200)
        self.layout().addWidget(self.input_username)

        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Password")
        self.input_password.setMaxLength(50)
        self.input_password.setMaximumWidth(200)
        self.layout().addWidget(self.input_password)

        signin_button = QPushButton("Sign in")
        signin_button.setMaximumWidth(100)
        signin_button.clicked.connect(self.login_attempt)
        self.layout().addWidget(signin_button)

        self.login_layout.addStretch()

        self.error_label = QLabel(self)
        self.error_label.setText("")
        self.layout().addWidget(self.error_label)

    def login_attempt(self):
        username = self.input_username.text()
        password = self.input_password.text()
        if not (username and password):
            self.show_error("Error: username or password is empty")
            return
        req_json = {
            'type': 'login',
            'username': username,
            'password': password
        }
        try:
            req = json.dumps(req_json)
            self.client.client_socket.send(req.encode())
        except Exception as e:
            self.show_error("Error: " + str(e))
        # looping = True
        #
        #
        # while looping:
        #     looping = False
        #
        #     try:
        #         rsp = self.client.client_socket.recv(1024).decode()
        #         rsp_json = json.loads(rsp)
        #         if rsp_json['type'] == 'login_result':
        #             if rsp_json['login_result'] == 'success':
        #                 self.client.data = rsp_json
        #                 self.client.logged_in = True
        #                 self.start_page.start_tabs_widget.login_page_button.hide()
        #                 self.start_page.start_tabs_widget.signup_page_button.hide()
        #                 self.start_page.start_tabs_widget.logout_page_button.show()
        #                 if isinstance(self.parent, QStackedWidget):
        #                     self.parent.setCurrentIndex(2)
        #                 panel_button = self.start_page.parent.parent.parent().tabs_widget.panel_button
        #                 if isinstance(panel_button, QPushButton):
        #                     panel_button.show()
        #                 vf = self.start_page.parent.parent.parent().stacked_widget.panel_widget.agent_panel.viewfile_tab
        #                 if isinstance(vf, ViewFileWidget):
        #                     vf.update_file_lists()
        #             else:
        #                 self.show_error(f"Error: {rsp_json['login_result']}")
        #         else:
        #             looping = True
        #     except socket.timeout:
        #         looping = True
        #     except Exception as e:
        #         self.show_error("Error: " + str(e))

    def show_error(self, error):
        self.error_label.setText(error)
        self.error_label.setStyleSheet("color: red")
    def show_message(self, message):
        self.error_label.setText(message)
        self.error_label.setStyleSheet("color: white")