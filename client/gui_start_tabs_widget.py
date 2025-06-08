from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class StartTabsWidget(QWidget):
    page = {
        "login": 0,
        "signup": 1,
        "logout": 2,
    }
    def __init__(self, start_widget, parent=None):
        super().__init__(parent)
        self.start_widget = start_widget
        self.setLayout(QHBoxLayout())

        self.login_page_button = QPushButton('Log In Page', parent=self)
        self.login_page_button.setMinimumHeight(50)
        self.login_page_button.clicked.connect(self.login_page)
        self.layout().addWidget(self.login_page_button)

        self.signup_page_button = QPushButton('Sign Up Page', parent=self)
        self.signup_page_button.setMinimumHeight(50)
        self.signup_page_button.clicked.connect(self.signup_page)
        self.layout().addWidget(self.signup_page_button)

        self.logout_page_button = QPushButton('Log Out Page', parent=self)
        self.logout_page_button.setMinimumHeight(50)
        self.logout_page_button.clicked.connect(self.logout_page)
        self.layout().addWidget(self.logout_page_button)
        self.logout_page_button.hide()

    def login_page(self):
        self.start_widget.setCurrentIndex(self.page["login"])
    def signup_page(self):
        self.start_widget.setCurrentIndex(self.page["signup"])
    def logout_page(self):
        self.start_widget.setCurrentIndex(self.page["logout"])