import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import StringVar, BooleanVar, END
from baku.core.backup_finder import BackupFinder
from baku.core.backup_restorer import BackupRestorer
from baku.core.file_queue import FileQueueItem, FileStatus
from baku.core.multi_file_manager import MultiFileManager
from loguru import logger
import time, json
from pathlib import Path

class BakUGUI:
    def __init__(self, root):
        self.root = root
        self.auto_mode = BooleanVar(value=True)
        self.theme_color = StringVar(value="#4a90e2")
        self._setup_ui()

    def _setup_ui(self):
        self.root.title("BakU 文件拖拽恢复工具")
        style = tb.Style(theme="flatly")
        style.configure("TFrame", background="#f4f6fa")
        main = tb.Frame(self.root, padding=20)
        main.pack(fill=BOTH, expand=YES)

        # 主题色选择
        theme_row = tb.Frame(main)
        theme_row.pack(fill=X, pady=4)
        tb.Label(theme_row, text="主题色:").pack(side=LEFT)
        color_entry = tb.Entry(theme_row, textvariable=self.theme_color, width=10)
        color_entry.pack(side=LEFT, padx=4)
        tb.Button(theme_row, text="应用", command=self._apply_theme).pack(side=LEFT)
        self._apply_theme()

        # 自动模式开关
        auto_row = tb.Frame(main)
        auto_row.pack(fill=X, pady=4)
        tb.Checkbutton(auto_row, text="自动模式(优先bak)", variable=self.auto_mode, bootstyle=SUCCESS).pack(side=LEFT)

        # 拖拽区
        drop_label = tb.Label(main, text="拖拽文件到这里，或点击选择", bootstyle=INFO, anchor=CENTER, font=("Segoe UI", 14), padding=20)
        drop_label.pack(fill=X, pady=10)
        drop_label.drop_target_register(DND_FILES)
        drop_label.dnd_bind('<<Drop>>', self.on_drop)
        tb.Button(main, text="选择文件", command=self._select_files).pack(pady=2)

        # 进度条
        self.progress = tb.Progressbar(main, mode="indeterminate")
        self.progress.pack(fill=X, pady=8)
        self.progress.stop()

        # 结果列表
        tb.Label(main, text="处理结果:").pack(anchor=W, pady=(8,0))
        self.result_box = tb.Treeview(main, columns=("file", "bak", "status", "msg"), show="headings", height=5)
        for col, txt in zip(["file", "bak", "status", "msg"], ["原文件", "bak路径", "状态", "消息"]):
            self.result_box.heading(col, text=txt)
            self.result_box.column(col, width=120 if col!="msg" else 200, anchor=W)
        self.result_box.pack(fill=X, pady=2)

        # 日志面板
        tb.Label(main, text="日志:").pack(anchor=W, pady=(8,0))
        self.log_text = tb.Text(main, height=7, bg="#222", fg="#0f0", font=("Consolas", 10))
        self.log_text.pack(fill=BOTH, expand=YES, pady=(0,8))

        # loguru日志同步
        logger.remove()
        logger.add(self._log_sink, level="INFO")

    def _apply_theme(self):
        color = self.theme_color.get()
        style = tb.Style()
        style.configure("TButton", background=color)
        style.configure("TCheckbutton", background="#f4f6fa")
        style.configure("TLabel", background="#f4f6fa")

    def _log_sink(self, msg):
        self.log_text.insert(END, str(msg) + "\n")
        self.log_text.see(END)

    def _select_files(self):
        from tkinter import filedialog
        files = filedialog.askopenfilenames()
        if files:
            self._process_files(list(files))

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        self._process_files(files)

    def _process_files(self, file_paths):
        self.progress.start()
        self.result_box.delete(*self.result_box.get_children())
        backup_finder = BackupFinder()
        backup_restorer = BackupRestorer()
        file_manager = MultiFileManager(backup_finder, backup_restorer)
        bak_trace = []
        for path in file_paths:
            p = Path(path)
            file_item = FileQueueItem(
                id=f"{p.name}_{p.stat().st_size}_{int(time.time())}",
                name=p.name,
                path=p,
                size=p.stat().st_size,
                status=FileStatus.PENDING,
                message="已添加到队列"
            )
            file_manager.file_queue.add_item(file_item)
        results = []
        for item in file_manager.file_queue.items:
            bak_path = None
            bak_candidate = item.path.with_suffix(item.path.suffix + '.bak')
            if self.auto_mode.get() and bak_candidate.exists():
                bak_path = str(bak_candidate)
                try:
                    backup_restorer.restore_backup(bak_candidate, item.path)
                    status = 'success'
                    msg = f'优先用同目录bak恢复: {bak_path}'
                except Exception as e:
                    status = 'error'
                    msg = f'bak恢复失败: {e}'
            else:
                found = backup_finder.find_nearest_backup(item.path)
                if found:
                    bak_path = str(found)
                    try:
                        backup_restorer.restore_backup(found, item.path)
                        status = 'success'
                        msg = f'回溯bak恢复: {bak_path}'
                    except Exception as e:
                        status = 'error'
                        msg = f'回溯bak恢复失败: {e}'
                else:
                    status = 'error'
                    msg = '未找到bak文件'
            bak_trace.append({'file': str(item.path), 'bak': bak_path})
            self.result_box.insert('', END, values=(str(item.path), bak_path or '', status, msg))
            results.append({'file': str(item.path), 'bak_used': bak_path, 'status': status, 'message': msg})
        logger.info(f"拖入文件与bak追踪: {json.dumps(bak_trace, ensure_ascii=False)}")
        self.progress.stop()

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = BakUGUI(root)
    root.mainloop() 