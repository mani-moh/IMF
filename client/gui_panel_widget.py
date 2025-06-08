from PySide6.QtWidgets import QStackedWidget

from gui_agent_panel import AgentPanel
from gui_secretary_panel import SecretaryPanel


class PanelWidget(QStackedWidget):
    page = {
        "secretary": 0,
        "agent": 1,
    }
    def __init__(self,client, parent):
        super().__init__(parent)
        self.client = client
        self.secretary_panel = SecretaryPanel(self)
        self.addWidget(self.secretary_panel)

        self.agent_panel = AgentPanel(self.client, self)
        self.addWidget(self.agent_panel)
