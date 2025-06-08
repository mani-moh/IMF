from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget
import socket, json
from gui_viewfile_widget import ViewFileWidget

class LogoutPage(QWidget):
    def __init__(self, client, start_page, parent=None):
        super(LogoutPage, self).__init__(parent)
        self.client = client
        self.parent = parent
        self.start_page = start_page
        self.logout_layout = QVBoxLayout()
        self.setLayout(self.logout_layout)

        self.logout_button = QPushButton('Logout')
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setMinimumHeight(100)
        self.logout_layout.addWidget(self.logout_button)

        self.logout_layout.addStretch()

        self.error_label = QLabel(self)
        self.error_label.setText("")
        self.layout().addWidget(self.error_label)

    def logout(self):
        req_json = {
            "type": "logout",
        }
        req = json.dumps(req_json)
        self.client.client_socket.send(req.encode())
        username = self.client.data["username"]
        self.client.data = {}
        self.client.logged_in = False
        self.start_page.start_tabs_widget.login_page_button.show()
        self.start_page.start_tabs_widget.signup_page_button.show()
        self.start_page.start_tabs_widget.logout_page_button.hide()
        if isinstance(self.parent, QStackedWidget):
            self.parent.setCurrentIndex(0)
        panel_button = self.start_page.parent.parent.parent().tabs_widget.panel_button
        if isinstance(panel_button, QPushButton):
            panel_button.hide()
        vf = self.start_page.parent.parent.parent().stacked_widget.panel_widget.agent_panel.viewfile_tab
        if isinstance(vf, ViewFileWidget):
            vf.update_file_lists()

    def show_error(self, error):
        self.error_label.setText(error)
        self.error_label.setStyleSheet("color: red")

    def show_message(self, message):
        self.error_label.setText(message)
        self.error_label.setStyleSheet("color: white")