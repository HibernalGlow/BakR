from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QLabel
from PyQt5.QtCore import Qt

class QueuePanel(QWidget):
    def __init__(self, theme=None):
        super().__init__()
        self.theme = theme or {}
        self.file_list = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel('文件队列管理区')
        label.setStyleSheet(f"color: {self.theme.get('fg', '#fff')}; font-size: 20px; font-weight: bold;")
        layout.addWidget(label)
        btn_add = QPushButton('添加文件')
        btn_add.setStyleSheet(f"background-color: {self.theme.get('accent', '#7aa2f7')}; color: {self.theme.get('bg', '#1a1b26')}; font-size: 15px; border-radius: 6px; padding: 8px 0;")
        btn_add.clicked.connect(self.add_files)
        layout.addWidget(btn_add)
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"background-color: {self.theme.get('bg', '#1a1b26')}; color: {self.theme.get('fg', '#c0caf5')}; border: 1px solid {self.theme.get('border', '#3b4261')}; font-size: 13px;")
        layout.addWidget(self.list_widget)
        # 拖拽支持（预留接口）
        # self.setAcceptDrops(True)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, '选择文件', '', '所有文件 (*)')
        for f in files:
            if f not in self.file_list:
                self.file_list.append(f)
                self.list_widget.addItem(f)

    # def dragEnterEvent(self, event):
    #     if event.mimeData().hasUrls():
    #         event.acceptProposedAction()
    #
    # def dropEvent(self, event):
    #     for url in event.mimeData().urls():
    #         f = url.toLocalFile()
    #         if f and f not in self.file_list:
    #             self.file_list.append(f)
    #             self.list_widget.addItem(f) 