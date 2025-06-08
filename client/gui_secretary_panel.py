from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout


class SecretaryPanel(QWidget):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.Secretary_layout = QVBoxLayout()
        self.setLayout(self.Secretary_layout)
