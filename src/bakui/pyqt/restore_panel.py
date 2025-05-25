from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget

class RestorePanel(QWidget):
    def __init__(self, theme=None):
        super().__init__()
        self.theme = theme or {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel('恢复文件区')
        label.setStyleSheet(f"color: {self.theme.get('fg', '#fff')}; font-size: 20px; font-weight: bold;")
        layout.addWidget(label)
        btn_restore = QPushButton('批量恢复')
        btn_restore.setStyleSheet(f"background-color: {self.theme.get('accent', '#7aa2f7')}; color: {self.theme.get('bg', '#1a1b26')}; font-size: 15px; border-radius: 6px; padding: 8px 0;")
        layout.addWidget(btn_restore)
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"background-color: {self.theme.get('bg', '#1a1b26')}; color: {self.theme.get('fg', '#c0caf5')}; border: 1px solid {self.theme.get('border', '#3b4261')}; font-size: 13px;")
        layout.addWidget(self.list_widget) 