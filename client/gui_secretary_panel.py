from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from gui_mfile_widget import MFileWidget


class SecretaryPanel(QWidget):
    def __init__(self, client, agent_panel, parent=None):
        super().__init__(parent)
        self.client = client
        self.agent_panel = agent_panel
        self.secretary_layout = QVBoxLayout()
        self.setLayout(self.secretary_layout)

        self.secretary_layout.addWidget(self.agent_panel)

        self.mfile_tab = MFileWidget(self.client, self.agent_panel)
        self.agent_panel.agent_tabs.addTab(self.mfile_tab, 'Manage Files')
        self.agent_panel.agent_tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if index == 2:
            self.mfile_tab.update_file_lists()