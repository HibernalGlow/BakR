from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class StatsPanel(QWidget):
    def __init__(self, file_manager=None, theme=None):
        super().__init__()
        self.theme = theme or {}
        self.file_manager = file_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel('统计信息区')
        label.setStyleSheet(f"color: {self.theme.get('fg', '#fff')}; font-size: 20px; font-weight: bold;")
        layout.addWidget(label)
        # TODO: 统计信息展示 