from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit, QMessageBox
from PyQt5.QtCore import Qt

class RestorePanel(QWidget):
    def __init__(self, file_manager=None, theme=None):
        super().__init__()
        self.theme = theme or {}
        self.file_manager = file_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel('恢复文件区')
        label.setStyleSheet(f"color: {self.theme.get('fg', '#fff')}; font-size: 20px; font-weight: bold;")
        layout.addWidget(label)
        btn_restore = QPushButton('批量恢复')
        btn_restore.setStyleSheet(f"background-color: {self.theme.get('accent', '#7aa2f7')}; color: {self.theme.get('bg', '#1a1b26')}; font-size: 15px; border-radius: 6px; padding: 8px 0;")
        btn_restore.clicked.connect(self.start_restore)
        layout.addWidget(btn_restore)
        self.progress = QProgressBar()
        self.progress.setStyleSheet(f"QProgressBar {{background: {self.theme.get('bg', '#1a1b26')}; color: {self.theme.get('fg', '#c0caf5')}; border: 1px solid {self.theme.get('border', '#3b4261')};}} QProgressBar::chunk {{background: {self.theme.get('accent', '#7aa2f7')};}}")
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.status_label = QLabel('')
        layout.addWidget(self.status_label)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

    def start_restore(self):
        if not self.file_manager:
            QMessageBox.warning(self, '错误', '未初始化文件管理器')
            return
        queue = self.file_manager.file_queue
        restorable = [item for item in queue.items if item.status.value == '可恢复']
        if not restorable:
            self.status_label.setText('没有可恢复的文件')
            return
        self.progress.setValue(0)
        self.status_label.setText('正在恢复...')
        self.result_text.clear()
        def progress_callback(progress, message):
            self.progress.setValue(int(progress * 100))
            self.status_label.setText(message)
        self.file_manager.set_progress_callback(progress_callback)
        success = self.file_manager.batch_restore_files()
        if success:
            self.status_label.setText('恢复完成')
            self.result_text.setText('\n'.join([f"{item.name}: {item.message}" for item in queue.items]))
        else:
            self.status_label.setText('恢复失败') 