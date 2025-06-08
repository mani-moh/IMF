from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class TabsWidget(QWidget):
    page = {
        "start": 0,
        "panel": 1,
    }
    panel_page = {
        "secretary": 0,
        "agent": 1,
    }
    def __init__(self,stacked_widget, client, parent=None ):
        super().__init__(parent)
        self.client = client
        self.stacked_widget = stacked_widget
        self.setLayout(QHBoxLayout())

        self.start_page_button = QPushButton('Account', parent=self)
        self.start_page_button.setMinimumHeight(50)
        self.start_page_button.clicked.connect(self.start_page)
        self.layout().addWidget(self.start_page_button)

        self.panel_button = QPushButton('Panel', parent=self)
        self.panel_button.setMinimumHeight(50)
        self.panel_button.clicked.connect(self.panel)
        self.layout().addWidget(self.panel_button)
        self.panel_button.hide()

    def start_page(self):
        self.stacked_widget.setCurrentIndex(self.page["start"])

    def panel(self):
        self.stacked_widget.setCurrentIndex(self.page["panel"])
        if self.client.data["user_type"] == "secretary":
            self.stacked_widget.panel_widget.setCurrentIndex(self.panel_page["secretary"])
        elif self.client.data["user_type"] == "agent":
            self.stacked_widget.panel_widget.setCurrentIndex(self.panel_page["agent"])



