from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QLabel, QHBoxLayout, QMessageBox, QMenu
from PyQt5.QtCore import Qt, QEvent
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
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton('添加文件')
        btn_add.setStyleSheet(f"background-color: {self.theme.get('accent', '#7aa2f7')}; color: {self.theme.get('bg', '#1a1b26')}; font-size: 15px; border-radius: 6px; padding: 8px 0;")
        btn_add.clicked.connect(self.add_files)
        btn_layout.addWidget(btn_add)
        
        btn_remove = QPushButton('移除选中')
        btn_remove.clicked.connect(self.remove_selected)
        btn_layout.addWidget(btn_remove)
        
        btn_clear = QPushButton('清空队列')
        btn_clear.clicked.connect(self.clear_queue)
        btn_layout.addWidget(btn_clear)
        
        btn_save = QPushButton('保存队列')
        btn_save.clicked.connect(self.save_queue)
        btn_layout.addWidget(btn_save)
        
        btn_load = QPushButton('加载队列')
        btn_load.clicked.connect(self.load_queue)
        btn_layout.addWidget(btn_load)
        
        layout.addLayout(btn_layout)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['文件名', '大小', '状态', '消息'])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)

        self.status_label = QLabel('')
        layout.addWidget(self.status_label)
        self.refresh_table()

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
        added = 0
        for f in files:
            path = Path(f)
            if f not in self.file_list:
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
                    added += 1
        self.status_label.setText(f"已添加 {added} 个文件到队列")
        self.refresh_table()

    def refresh_table(self):
        queue = self.file_manager.file_queue
        self.table.setRowCount(0)
        for item in queue.items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item.name))
            self.table.setItem(row, 1, QTableWidgetItem(self.format_file_size(item.size)))
            self.table.setItem(row, 2, QTableWidgetItem(item.status.value))
            self.table.setItem(row, 3, QTableWidgetItem(item.message))

    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        p = 1
        while size_bytes >= 1024 and i < len(size_names)-1:
            size_bytes /= 1024
            i += 1
        return f"{round(size_bytes,2)} {size_names[i]}"

    def remove_selected(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            self.status_label.setText("未选中任何文件")
            return
        rows = sorted([s.row() for s in selected], reverse=True)
        for row in rows:
            name = self.table.item(row, 0).text()
            self.file_manager.file_queue.remove_by_name(name)
            del self.file_list[row]
            self.table.removeRow(row)
        self.status_label.setText("已移除选中文件")
        self.refresh_table()

    def clear_queue(self):
        self.file_manager.file_queue.clear()
        self.file_list.clear()
        self.status_label.setText("队列已清空")
        self.refresh_table()

    def save_queue(self):
        path, _ = QFileDialog.getSaveFileName(self, '保存队列', '', '队列文件 (*.queue)')
        if path:
            self.file_manager.file_queue.save(path)
            self.status_label.setText(f"队列已保存到 {path}")

    def load_queue(self):
        path, _ = QFileDialog.getOpenFileName(self, '加载队列', '', '队列文件 (*.queue)')
        if path:
            self.file_manager.file_queue.load(path)
            self.file_list = [str(item.path) for item in self.file_manager.file_queue.items]
            self.status_label.setText(f"已加载队列 {path}")
            self.refresh_table()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        remove_action = menu.addAction('移除选中')
        action = menu.exec_(self.table.mapToGlobal(pos))
        if action == remove_action:
            self.remove_selected() 