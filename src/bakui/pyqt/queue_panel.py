from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QLabel
from PyQt5.QtCore import Qt
from pathlib import Path
import os

from baku.core.file_queue import FileQueueItem, FileStatus

class QueuePanel(QWidget):
    def __init__(self, file_manager, theme=None):
        super().__init__()
        self.theme = theme or {}
        self.file_manager = file_manager
        self.file_list = []
        self.init_ui()
        self.setAcceptDrops(True)

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

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, '选择文件', '', '所有文件 (*)')
        self._add_files_to_queue(files)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            f = url.toLocalFile()
            if f and os.path.isfile(f):
                files.append(f)
        self._add_files_to_queue(files)

    def _add_files_to_queue(self, files):
        for f in files:
            path = Path(f)
            if f not in self.file_list:
                # 构造FileQueueItem并添加到核心队列
                item = FileQueueItem(
                    id=f"{path.name}_{path.stat().st_size}_{int(path.stat().st_mtime)}",
                    name=path.name,
                    path=path,
                    size=path.stat().st_size,
                    status=FileStatus.PENDING,
                    message="已添加到队列"
                )
                if self.file_manager.file_queue.add_item(item):
                    self.file_list.append(f)
                    self.list_widget.addItem(f) 