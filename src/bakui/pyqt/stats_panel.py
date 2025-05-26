from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout

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
        self.grid = QGridLayout()
        layout.addLayout(self.grid)
        self.labels = {}
        stats = ['总文件数', '已扫描', '可恢复', '已恢复', '失败']
        for i, s in enumerate(stats):
            l1 = QLabel(s+':')
            l2 = QLabel('0')
            self.grid.addWidget(l1, i, 0)
            self.grid.addWidget(l2, i, 1)
            self.labels[s] = l2
        self.refresh_stats()

    def refresh_stats(self):
        if not self.file_manager:
            return
        queue = self.file_manager.file_queue
        total = len(queue.items)
        scanned = len([i for i in queue.items if i.status.value != '待处理'])
        restorable = len([i for i in queue.items if i.status.value == '可恢复'])
        restored = len([i for i in queue.items if i.status.value == '已恢复'])
        failed = len([i for i in queue.items if i.status.value == '失败'])
        self.labels['总文件数'].setText(str(total))
        self.labels['已扫描'].setText(str(scanned))
        self.labels['可恢复'].setText(str(restorable))
        self.labels['已恢复'].setText(str(restored))
        self.labels['失败'].setText(str(failed)) 