import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog
from baku.core.backup_finder import BackupFinder
from baku.core.backup_restorer import BackupRestorer
from baku.core.file_queue import FileQueueItem, FileStatus
from baku.core.multi_file_manager import MultiFileManager
import time, json
from pathlib import Path

class ActionPanel(tb.Frame):
    def __init__(self, master, main_app):
        super().__init__(master, bootstyle="light")
        self.main_app = main_app
        
        # 左侧：文件操作按钮
        file_frame = tb.LabelFrame(self, text="文件操作", bootstyle="primary", padding=10)
        file_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))
        
        # 添加文件按钮
        tb.Button(
            file_frame, 
            text="📁 添加文件", 
            bootstyle="primary", 
            command=self.add_files,
            width=12
        ).pack(pady=2, fill=X)
        
        # 添加文件夹按钮
        tb.Button(
            file_frame, 
            text="📂 添加文件夹", 
            bootstyle="primary-outline", 
            command=self.add_folder,
            width=12
        ).pack(pady=2, fill=X)
        
        # 中间：队列操作按钮
        queue_frame = tb.LabelFrame(self, text="队列操作", bootstyle="info", padding=10)
        queue_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))
        
        # 扫描备份按钮
        tb.Button(
            queue_frame, 
            text="🔍 扫描备份", 
            bootstyle="info", 
            command=self.scan_all_backups,
            width=12
        ).pack(pady=2, fill=X)
        
        # 批量恢复按钮  
        tb.Button(
            queue_frame, 
            text="🔄 批量恢复", 
            bootstyle="success", 
            command=self.restore_all,
            width=12
        ).pack(pady=2, fill=X)
        
        # 恢复选中按钮
        tb.Button(
            queue_frame, 
            text="✅ 恢复选中", 
            bootstyle="success-outline", 
            command=self.restore_selected,
            width=12
        ).pack(pady=2, fill=X)
        
        # 右侧：管理操作按钮
        manage_frame = tb.LabelFrame(self, text="管理操作", bootstyle="warning", padding=10)
        manage_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))
        
        # 移除选中按钮
        tb.Button(
            manage_frame, 
            text="❌ 移除选中", 
            bootstyle="warning", 
            command=self.remove_selected,
            width=12
        ).pack(pady=2, fill=X)
        
        # 清空队列按钮
        tb.Button(
            manage_frame, 
            text="🗑️ 清空队列", 
            bootstyle="danger", 
            command=self.clear_queue,
            width=12
        ).pack(pady=2, fill=X)
        
        # 最右侧：统计信息
        stats_frame = tb.LabelFrame(self, text="队列统计", bootstyle="secondary", padding=10)
        stats_frame.pack(side=RIGHT, fill=BOTH, expand=YES)
        
        self.stats_label = tb.Label(
            stats_frame, 
            text="总计: 0\n待处理: 0\n处理中: 0\n成功: 0\n失败: 0", 
            bootstyle="secondary",
            font=("Segoe UI", 9),
            justify=LEFT,
            width=15
        )
        self.stats_label.pack(fill=BOTH, expand=YES)
        
        # 定时更新统计
        self.update_stats()
    
    def add_files(self):
        """添加文件到队列"""
        files = filedialog.askopenfilenames(
            title="选择文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("Python文件", "*.py"),
                ("文本文件", "*.txt"),
                ("配置文件", "*.json;*.yaml;*.yml;*.ini;*.conf")
            ]
        )
        
        if files:
            self.main_app.add_files_to_queue(files)
            self.main_app.log_panel.log(f"添加了 {len(files)} 个文件", "INFO")
            self.update_stats()
    
    def add_folder(self):
        """添加文件夹中的所有文件"""
        folder = filedialog.askdirectory(title="选择文件夹")
        
        if folder:
            folder_path = Path(folder)
            files = []
            
            # 递归查找所有文件
            for file_path in folder_path.rglob("*"):
                if file_path.is_file():
                    files.append(str(file_path))
            
            if files:
                self.main_app.add_files_to_queue(files)
                self.main_app.log_panel.log(f"从文件夹添加了 {len(files)} 个文件", "INFO")
                self.update_stats()
            else:
                self.main_app.log_panel.log("文件夹中没有找到文件", "WARNING")
    
    def scan_all_backups(self):
        """扫描队列中所有文件的备份"""
        queue_items = list(self.main_app.file_manager.file_queue.items)
        
        if not queue_items:
            self.main_app.log_panel.log("队列为空，请先添加文件", "WARNING")
            return
        
        self.main_app.progress.start()
        self.main_app.log_panel.log(f"开始扫描 {len(queue_items)} 个文件的备份...", "INFO")
        
        try:
            found_count = 0
            for item in queue_items:
                try:
                    # 检查同目录 .bak 文件
                    bak_candidate = item.path.with_suffix(item.path.suffix + '.bak')
                    if bak_candidate.exists():
                        item.message = f"同目录备份: {bak_candidate.name}"
                        found_count += 1
                        self.main_app.log_panel.log(f"✓ {item.name} 找到同目录备份", "SUCCESS")
                    else:
                        # 查找其他备份
                        found_backup = self.main_app.backup_finder.find_nearest_backup(item.path)
                        if found_backup:
                            item.message = f"找到备份: {found_backup.name}"
                            found_count += 1
                            self.main_app.log_panel.log(f"✓ {item.name} 找到备份: {found_backup}", "SUCCESS")
                        else:
                            item.message = "未找到备份文件"
                            self.main_app.log_panel.log(f"⚠ {item.name} 未找到备份", "WARNING")
                    
                    self.main_app.queue_panel.update_file_item(item)
                    
                except Exception as e:
                    item.message = f"扫描失败: {e}"
                    self.main_app.log_panel.log(f"✗ {item.name} 扫描失败: {e}", "ERROR")
                    self.main_app.queue_panel.update_file_item(item)
            
            self.main_app.log_panel.log(f"扫描完成！找到 {found_count}/{len(queue_items)} 个备份", "SUCCESS")
            self.update_stats()
            
        finally:
            self.main_app.progress.stop()
    
    def restore_all(self):
        """批量恢复队列中的所有文件"""        
        queue_items = [item for item in self.main_app.file_manager.file_queue.items 
              if item.status in [FileStatus.PENDING, FileStatus.ERROR]]
        
        if not queue_items:
            self.main_app.log_panel.log("没有需要恢复的文件", "WARNING")
            return
        
        self.main_app.progress.start()
        self.main_app.log_panel.log(f"开始批量恢复 {len(queue_items)} 个文件...", "INFO")
        
        try:
            success_count = 0
            for item in queue_items:
                item.status = FileStatus.PROCESSING
                self.main_app.queue_panel.update_file_item(item)
                
                result = self.main_app._process_single_file(item)
                self.main_app.queue_panel.update_file_item(item)
                
                if result['status'] == 'success':
                    success_count += 1
            
            self.main_app.log_panel.log(f"批量恢复完成！成功: {success_count}/{len(queue_items)}", "SUCCESS")
            self.update_stats()
            
        finally:
            self.main_app.progress.stop()
    
    def restore_selected(self):
        """恢复选中的文件"""
        self.main_app.queue_panel.restore_selected()
        self.update_stats()
    
    def remove_selected(self):
        """移除选中的文件"""
        self.main_app.queue_panel.remove_selected()
        self.update_stats()
    
    def clear_queue(self):
        """清空队列"""
        self.main_app.queue_panel.clear_queue()
        self.update_stats()
    
    def update_stats(self):
        """更新队列统计信息"""
        try:
            queue_items = list(self.main_app.file_manager.file_queue.items)
            total = len(queue_items)
            
            pending = sum(1 for item in queue_items if item.status == FileStatus.PENDING)
            processing = sum(1 for item in queue_items if item.status == FileStatus.PROCESSING)
            success = sum(1 for item in queue_items if item.status == FileStatus.COMPLETED)
            failed = sum(1 for item in queue_items if item.status == FileStatus.ERROR)
            skipped = sum(1 for item in queue_items if item.status == FileStatus.CANCELLED)
            
            stats_text = f"总计: {total}\n待处理: {pending}\n处理中: {processing}\n成功: {success}\n失败: {failed}"
            if skipped > 0:
                stats_text += f"\n跳过: {skipped}"
            
            self.stats_label.config(text=stats_text)
            
            # 更快速度更新（每0.5秒）
            self.after(500, self.update_stats)
            
            # 通知队列面板更新显示
            self.main_app.queue_panel.update_colors()
            
        except Exception as e:
            # 如果出错，显示基本信息
            self.stats_label.config(text="总计: 0\n待处理: 0\n处理中: 0\n成功: 0\n失败: 0")