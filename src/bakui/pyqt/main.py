import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

from bakui.pyqt.queue_panel import QueuePanel
from bakui.pyqt.scan_panel import ScanPanel
from bakui.pyqt.restore_panel import RestorePanel
from bakui.pyqt.stats_panel import StatsPanel

# Tokyonight主题色
TOKYONIGHT = {
    'bg': '#1a1b26',
    'fg': '#c0caf5',
    'accent': '#7aa2f7',
    'button': '#414868',
    'button_hover': '#7aa2f7',
    'border': '#3b4261'
}

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('baku 智能备份恢复工具 - GUI (PyQt)')
        self.resize(900, 600)
        self.setFont(QFont('微软雅黑', 10))
        self.setStyleSheet(f"background-color: {TOKYONIGHT['bg']}; color: {TOKYONIGHT['fg']};")
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        # 左侧导航栏
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(30)
        nav_layout.setContentsMargins(20, 40, 10, 40)
        btn_style = f'''
            QPushButton {{
                background-color: {TOKYONIGHT['button']};
                color: {TOKYONIGHT['fg']};
                border: none;
                border-radius: 8px;
                padding: 12px 0;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {TOKYONIGHT['button_hover']};
                color: {TOKYONIGHT['bg']};
            }}
        '''
        self.btn_queue = QPushButton('文件队列')
        self.btn_scan = QPushButton('扫描备份')
        self.btn_restore = QPushButton('恢复文件')
        self.btn_stats = QPushButton('统计信息')
        for btn in [self.btn_queue, self.btn_scan, self.btn_restore, self.btn_stats]:
            btn.setStyleSheet(btn_style)
            nav_layout.addWidget(btn)
        nav_layout.addStretch(1)
        # 右侧功能区
        self.stack = QStackedWidget()
        self.panels = {
            'queue': QueuePanel(theme=TOKYONIGHT),
            'scan': ScanPanel(theme=TOKYONIGHT),
            'restore': RestorePanel(theme=TOKYONIGHT),
            'stats': StatsPanel(theme=TOKYONIGHT)
        }
        for p in self.panels.values():
            self.stack.addWidget(p)
        # 绑定切换
        self.btn_queue.clicked.connect(lambda: self.stack.setCurrentWidget(self.panels['queue']))
        self.btn_scan.clicked.connect(lambda: self.stack.setCurrentWidget(self.panels['scan']))
        self.btn_restore.clicked.connect(lambda: self.stack.setCurrentWidget(self.panels['restore']))
        self.btn_stats.clicked.connect(lambda: self.stack.setCurrentWidget(self.panels['stats']))
        # 默认显示队列
        self.stack.setCurrentWidget(self.panels['queue'])
        # 布局
        main_layout.addLayout(nav_layout, 1)
        main_layout.addWidget(self.stack, 4)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 