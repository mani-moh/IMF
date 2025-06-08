from PySide6.QtWidgets import QWidget,QVBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel
from PySide6.QtCore import Qt
import json

class SignupPage(QWidget):
    def __init__(self, client, start_page, parent=None):
        super(SignupPage, self).__init__(parent)
        minimum = 20
        self.client = client
        self.parent = parent
        self.start_page = start_page
        self.signup_layout = QVBoxLayout()
        self.setLayout(self.signup_layout)

        self.input_type = QLineEdit(self)
        self.input_type.setPlaceholderText("type")
        self.input_type.setMaxLength(50)
        self.input_type.setMaximumWidth(200)
        self.input_type.setMinimumHeight(minimum)
        self.signup_layout.addWidget(self.input_type, 0, Qt.AlignmentFlag.AlignHCenter)

        self.input_firstname = QLineEdit(self)
        self.input_firstname.setPlaceholderText("firstname")
        self.input_firstname.setMaxLength(50)
        self.input_firstname.setMaximumWidth(200)
        self.input_firstname.setMinimumHeight(minimum)
        self.signup_layout.addWidget(self.input_firstname, 0, Qt.AlignmentFlag.AlignHCenter)

        self.input_lastname = QLineEdit(self)
        self.input_lastname.setPlaceholderText("lastname")
        self.input_lastname.setMaxLength(50)
        self.input_lastname.setMaximumWidth(200)
        self.input_firstname.setMinimumHeight(minimum)
        self.signup_layout.addWidget(self.input_lastname, 0, Qt.AlignmentFlag.AlignHCenter)

        self.input_username = QLineEdit(self)
        self.input_username.setPlaceholderText("username")
        self.input_username.setMaxLength(50)
        self.input_username.setMaximumWidth(200)
        self.input_firstname.setMinimumHeight(minimum)
        self.signup_layout.addWidget(self.input_username, 0, Qt.AlignmentFlag.AlignHCenter)

        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("password")
        self.input_password.setMaxLength(50)
        self.input_password.setMaximumWidth(200)
        self.input_password.setMinimumHeight(minimum)
        self.signup_layout.addWidget(self.input_password, 0, Qt.AlignmentFlag.AlignHCenter)

        self.input_access_p = QComboBox(self)
        self.input_access_p.setPlaceholderText("personnel access")
        self.input_access_p.addItem("False", 0)
        self.input_access_p.addItem("True", 1)
        self.input_access_p.setMinimumHeight(minimum)
        self.signup_layout.addWidget(self.input_access_p, 0, Qt.AlignmentFlag.AlignHCenter)

        self.input_access_n = QComboBox(self)
        self.input_access_n.setPlaceholderText("nuclear access")
        self.input_access_n.addItem("False", 0)
        self.input_access_n.addItem("True", 1)
        self.input_access_n.setMinimumHeight(minimum)
        self.signup_layout.addWidget(self.input_access_n, 0, Qt.AlignmentFlag.AlignHCenter)

        self.input_access_b = QComboBox(self)
        self.input_access_b.setPlaceholderText("bio access")
        self.input_access_b.addItem("False", 0)
        self.input_access_b.addItem("True", 1)
        self.input_access_b.setMinimumHeight(minimum)
        self.signup_layout.addWidget(self.input_access_b, 0, Qt.AlignmentFlag.AlignHCenter)

        signup_button = QPushButton("Sign in")
        signup_button.setMaximumWidth(100)
        signup_button.setMinimumHeight(minimum)
        signup_button.clicked.connect(self.signup_attempt)
        self.signup_layout.addWidget(signup_button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.signup_layout.addStretch()

        self.error_label = QLabel(self)
        self.error_label.setText("")
        self.signup_layout.addWidget(self.error_label)

    def signup_attempt(self):
        type = self.input_type.text()
        firstname = self.input_firstname.text()
        lastname = self.input_lastname.text()
        username = self.input_username.text()
        password = self.input_password.text()
        access_p = str(self.input_access_p.currentData())
        access_n = str(self.input_access_n.currentData())
        access_b = str(self.input_access_b.currentData())
        if not (type and firstname and lastname and username and password and access_p and access_n and access_b):
            self.show_error("Error: a field is empty")
            return
        req_json = {
            'type': 'signup',
            'username': username,
            'password': password,
            'first_name': firstname,
            'last_name': lastname,
            'user_type': type,
            'access_p': access_p,
            'access_n': access_n,
            'access_b': access_b
        }
        try:
            req = json.dumps(req_json)
            self.client.client_socket.send(req.encode())
        except Exception as e:
            self.show_error("Error: " + str(e))
        looping = True

        # while looping:
        #     looping = False
        #
        #     try:
        #         rsp = self.client.client_socket.recv(1024).decode()
        #         rsp_json = json.loads(rsp)
        #         if rsp_json['type'] == 'signup_result':
        #             if rsp_json['signup_result'] == 'success':
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
        #                 self.show_error(f"Error: {rsp_json['signup_result']}")
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