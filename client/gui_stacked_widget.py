from PySide6.QtWidgets import QStackedWidget


from gui_panel_widget import PanelWidget
from gui_start_page_widget import StartPageWidget


class StackedWidget(QStackedWidget):
    page = {
        "start": 0,
        "panel": 1
    }
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.client = client
        self.start_page_widget = StartPageWidget(self.client,self)
        self.addWidget(self.start_page_widget)

        self.panel_widget = PanelWidget(self.client, self)
        self.addWidget(self.panel_widget)

        self.setCurrentIndex(self.page["start"])