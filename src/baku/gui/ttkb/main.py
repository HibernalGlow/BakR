import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import StringVar, BooleanVar, END
from baku.core.backup_finder import BackupFinder
from baku.core.backup_restorer import BackupRestorer
from baku.core.file_queue import FileQueueItem, FileStatus
from baku.core.multi_file_manager import MultiFileManager
from loguru import logger
import time, json, re
from pathlib import Path

from baku.gui.ttkb.theme_panel import ThemePanel
from baku.gui.ttkb.queue_panel import QueuePanel
from baku.gui.ttkb.log_panel import LogPanel
from baku.gui.ttkb.action_panel import ActionPanel

class BakUGUI:
    def __init__(self, root):
        self.root = root
        self.auto_mode = BooleanVar(value=True)
        self.style = tb.Style(theme="superhero")  # 默认主题
        
        # 核心组件
        self.backup_finder = BackupFinder()
        self.backup_restorer = BackupRestorer()
        self.file_manager = MultiFileManager(self.backup_finder, self.backup_restorer)
        
        self._setup_ui()
        self._setup_logging()

    def _setup_ui(self):
        self.root.title("BakU - 智能备份文件恢复工具")
        self.root.geometry("1000x700")
        
        # 主容器
        main_container = tb.Frame(self.root, padding=10, bootstyle="light")
        main_container.pack(fill=BOTH, expand=YES)
        
        # 顶部：主题选择和自动模式
        top_frame = tb.Frame(main_container, bootstyle="light")
        top_frame.pack(fill=X, pady=(0, 10))
        
        # 主题切换
        self.theme_panel = ThemePanel(top_frame, self)
        self.theme_panel.pack(side=LEFT, padx=(0, 20))
        
        # 自动模式开关
        mode_frame = tb.Frame(top_frame, bootstyle="light")
        mode_frame.pack(side=LEFT)
        tb.Label(mode_frame, text="模式:", bootstyle="light").pack(side=LEFT, padx=(0, 5))
        self.auto_checkbox = tb.Checkbutton(
            mode_frame, 
            text="自动模式（拖拽即恢复）", 
            variable=self.auto_mode, 
            bootstyle="success-round-toggle"
        )
        self.auto_checkbox.pack(side=LEFT)
        
        # 拖拽区域
        drop_frame = tb.LabelFrame(main_container, text="拖拽区域", bootstyle="info", padding=10)
        drop_frame.pack(fill=X, pady=(0, 10))
        
        self.drop_label = tb.Label(
            drop_frame, 
            text="🎯 拖拽文件到这里，或使用下方按钮添加文件", 
            bootstyle="info",
            anchor=CENTER, 
            font=("Segoe UI", 12)
        )
        self.drop_label.pack(fill=X, pady=20)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)
        
        # 中部：操作按钮区
        self.action_panel = ActionPanel(main_container, self)
        self.action_panel.pack(fill=X, pady=(0, 10))
        
        # 进度条
        self.progress = tb.Progressbar(main_container, mode="indeterminate", bootstyle="info-striped")
        self.progress.pack(fill=X, pady=(0, 10))
        
        # 下部：队列和日志
        content_frame = tb.Frame(main_container, bootstyle="light")
        content_frame.pack(fill=BOTH, expand=YES)
        
        # 队列面板（左侧）
        queue_frame = tb.LabelFrame(content_frame, text="文件队列", bootstyle="secondary", padding=5)
        queue_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5))
        
        self.queue_panel = QueuePanel(queue_frame, self)
        self.queue_panel.pack(fill=BOTH, expand=YES)
        
        # 日志面板（右侧）
        log_frame = tb.LabelFrame(content_frame, text="操作日志", bootstyle="dark", padding=5)
        log_frame.pack(side=RIGHT, fill=Y, padx=(5, 0))
        log_frame.configure(width=300)
        
        self.log_panel = LogPanel(log_frame, self.style)
        self.log_panel.pack(fill=BOTH, expand=YES)

    def _setup_logging(self):
        """设置日志系统"""
        logger.remove()
        logger.add(self.log_panel.log, level="INFO")
        logger.info("BakU GUI 启动成功")

    def on_drop(self, event):
        """拖拽文件处理"""
        files = self.root.tk.splitlist(event.data)
        self.add_files_to_queue(files)
        
        if self.auto_mode.get():
            self.process_files_auto()

    def add_files_to_queue(self, file_paths):
        """添加文件到队列"""
        for path in file_paths:
            try:
                p = Path(path)
                if p.is_file():
                    file_item = FileQueueItem(
                        id=f"{p.name}_{p.stat().st_size}_{int(time.time())}",
                        name=p.name,
                        path=p,
                        size=p.stat().st_size,
                        status=FileStatus.PENDING,
                        message="已添加到队列"
                    )
                    self.file_manager.file_queue.add_item(file_item)
                    self.queue_panel.add_file_item(file_item)
                    logger.info(f"添加文件: {p.name}")
            except Exception as e:
                logger.error(f"添加文件失败 {path}: {e}")

    def process_files_auto(self):
        """自动模式处理文件"""
        self.progress.start()
        try:
            results = []
            for item in self.file_manager.file_queue.items:
                if item.status == FileStatus.PENDING:
                    result = self._process_single_file(item)
                    results.append(result)
                    self.queue_panel.update_file_item(item)
            
            logger.info(f"自动处理完成，处理了 {len(results)} 个文件")
        finally:
            self.progress.stop()    
    def _process_single_file(self, item):
        """处理单个文件"""
        try:            # 优先检查同目录 .bak 文件
            bak_candidate = item.path.with_suffix(item.path.suffix + '.bak')
            if bak_candidate.exists():
                # 修复参数顺序：第一个是目标文件，第二个是备份文件
                result = self.backup_restorer.restore_backup(item.path, bak_candidate)
                if result.get('success', False):
                    item.status = FileStatus.COMPLETED
                    item.message = f'从同目录bak恢复: {bak_candidate.name}'
                    logger.success(f"✓ {item.name} 恢复成功")
                    return {'status': 'success', 'file': str(item.path), 'bak': str(bak_candidate)}
                else:
                    item.status = FileStatus.ERROR
                    item.message = f'恢复失败: {result.get("message", "未知错误")}'
                    logger.error(f"✗ {item.name} 恢复失败: {result.get('message')}")
                    return {'status': 'error', 'file': str(item.path), 'error': result.get('message')}
              # 回溯查找备份文件
            found_backup = self.backup_finder.find_nearest_backup(item.path)
            if found_backup:
                # 修复参数顺序：第一个是目标文件，第二个是备份文件
                result = self.backup_restorer.restore_backup(item.path, found_backup)
                if result.get('success', False):
                    item.status = FileStatus.COMPLETED
                    item.message = f'从备份恢复: {found_backup.name}'
                    logger.success(f"✓ {item.name} 恢复成功")
                    return {'status': 'success', 'file': str(item.path), 'bak': str(found_backup)}
                else:
                    item.status = FileStatus.ERROR
                    item.message = f'恢复失败: {result.get("message", "未知错误")}'
                    logger.error(f"✗ {item.name} 恢复失败: {result.get('message')}")
                    return {'status': 'error', 'file': str(item.path), 'error': result.get('message')}
              # 未找到备份
            item.status = FileStatus.ERROR
            item.message = '未找到备份文件'
            logger.warning(f"⚠ {item.name} 未找到备份")
            return {'status': 'failed', 'file': str(item.path), 'bak': None}
            
        except Exception as e:
            item.status = FileStatus.ERROR
            item.message = f'恢复失败: {e}'
            logger.error(f"✗ {item.name} 恢复失败: {e}")
            return {'status': 'error', 'file': str(item.path), 'error': str(e)}

    def change_theme(self, theme_name):
        """切换主题"""
        self.style.theme_use(theme_name)
        self.log_panel.update_theme_colors()
        logger.info(f"主题已切换为: {theme_name}")

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = BakUGUI(root)
    root.mainloop()