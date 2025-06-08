from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget

from gui_viewfile_widget import ViewFileWidget


class AgentPanel(QWidget):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.agent_layout = QVBoxLayout()
        self.setLayout(self.agent_layout)

        self.label = QLabel(self)
        self.label.setText("Agent Panel")
        self.agent_layout.addWidget(self.label)

        self.agent_tabs = QTabWidget(self)
        self.agent_layout.addWidget(self.agent_tabs)

        self.viewfile_tab = ViewFileWidget(self.client, self)

        self.viewfile_label = QLabel(self.viewfile_tab)

        self.agent_tabs.addTab(self.viewfile_tab, "View Files")

        self.chat_tab = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_label = QLabel(self.chat_tab)
        self.chat_label.setText("Chat")
        self.chat_layout.addWidget(self.chat_label)
        self.chat_tab.setLayout(self.chat_layout)
        self.agent_tabs.addTab(self.chat_tab, "Chat")

        self.agent_tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if index == 0:
            self.viewfile_tab.update_file_lists()