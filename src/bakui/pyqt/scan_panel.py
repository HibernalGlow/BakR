from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar

class ScanPanel(QWidget):
    def __init__(self, file_manager=None, theme=None):
        super().__init__()
        self.theme = theme or {}
        self.file_manager = file_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel('扫描备份区')
        label.setStyleSheet(f"color: {self.theme.get('fg', '#fff')}; font-size: 20px; font-weight: bold;")
        layout.addWidget(label)
        btn_scan = QPushButton('开始扫描')
        btn_scan.setStyleSheet(f"background-color: {self.theme.get('accent', '#7aa2f7')}; color: {self.theme.get('bg', '#1a1b26')}; font-size: 15px; border-radius: 6px; padding: 8px 0;")
        layout.addWidget(btn_scan)
        self.progress = QProgressBar()
        self.progress.setStyleSheet(f"QProgressBar {{background: {self.theme.get('bg', '#1a1b26')}; color: {self.theme.get('fg', '#c0caf5')}; border: 1px solid {self.theme.get('border', '#3b4261')};}} QProgressBar::chunk {{background: {self.theme.get('accent', '#7aa2f7')};}}")
        self.progress.setValue(0)
        layout.addWidget(self.progress) 