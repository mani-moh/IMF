from PySide6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout

from gui_login_page import LoginPage
from gui_start_tabs_widget import StartTabsWidget
from gui_signup_page import SignupPage
from gui_logout_page import LogoutPage


class StartPageWidget(QWidget):

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.client = client
        self.setLayout(QVBoxLayout())

        self.start_stacked_widget = QStackedWidget(self)
        self.start_tabs_widget = StartTabsWidget(self.start_stacked_widget, self)


        self.layout().addWidget(self.start_tabs_widget)
        self.layout().addWidget(self.start_stacked_widget)

        self.login_page = LoginPage(self.client, self, self.start_stacked_widget)
        self.start_stacked_widget.addWidget(self.login_page)

        self.signup_page = SignupPage(self.client, self, self.start_stacked_widget)
        self.start_stacked_widget.addWidget(self.signup_page)

        self.logout_page = LogoutPage(self.client, self, self.start_stacked_widget)
        self.start_stacked_widget.addWidget(self.logout_page)



        self.start_stacked_widget.setCurrentIndex(0)
