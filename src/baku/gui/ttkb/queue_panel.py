import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES
from tkinter import Menu
from baku.core.file_queue import FileStatus

class QueuePanel(tb.Frame):
    def __init__(self, master, main_app):
        super().__init__(master, bootstyle="secondary")
        self.main_app = main_app
          # 队列树形视图
        self.tree = tb.Treeview(
            self, 
            columns=("name", "path", "status", "message"), 
            show="headings", 
            height=12,
            selectmode="extended"  # 支持多选
        )
        
        # 列标题和宽度
        columns_config = {
            "name": ("文件名", 150),
            "path": ("路径", 200),
            "status": ("状态", 80),
            "message": ("消息", 200)
        }
        
        for col, (text, width) in columns_config.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=W)
          # 滚动条
        v_scrollbar = tb.Scrollbar(self, orient="vertical", command=self.tree.yview)
        h_scrollbar = tb.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置权重
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 拖拽支持
        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind('<<Drop>>', self.on_drop)
        
        # 右键菜单
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="🔍 扫描备份", command=self.scan_selected)
        self.context_menu.add_command(label="🔄 恢复文件", command=self.restore_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ 移除选中", command=self.remove_selected)
        self.context_menu.add_command(label="🗑️ 清空队列", command=self.clear_queue)
        
        # 绑定右键菜单
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # 双击事件
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # 文件项映射（item_id -> FileQueueItem）
        self.file_items = {}
    
    def add_file_item(self, file_item):
        """添加文件项到队列"""        # 状态图标映射
        status_icons = {
            FileStatus.PENDING: "⏳",
            FileStatus.PROCESSING: "🔄",
            FileStatus.COMPLETED: "✅",
            FileStatus.ERROR: "❌",
            FileStatus.CANCELLED: "⏭️"
        }
        
        status_display = f"{status_icons.get(file_item.status, '❓')} {file_item.status.value}"
        
        item_id = self.tree.insert('', END, values=(
            file_item.name,
            str(file_item.path.parent),
            status_display,
            file_item.message
        ))
        
        # 保存文件项映射
        self.file_items[item_id] = file_item
        
        # 根据状态设置行颜色
        self._update_item_color(item_id, file_item.status)
        
        return item_id
    
    def update_file_item(self, file_item):
        """更新文件项状态"""
        # 查找对应的树项
        for item_id, stored_item in self.file_items.items():
            if stored_item.id == file_item.id:
                status_icons = {
                    FileStatus.PENDING: "⏳",
                    FileStatus.PROCESSING: "🔄",
                    FileStatus.SUCCESS: "✅",
                    FileStatus.FAILED: "❌",
                    FileStatus.SKIPPED: "⏭️"
                }
                
                status_display = f"{status_icons.get(file_item.status, '❓')} {file_item.status.value}"
                
                # 更新树项显示
                self.tree.item(item_id, values=(
                    file_item.name,
                    str(file_item.path.parent),
                    status_display,
                    file_item.message
                ))
                
                # 更新颜色
                self._update_item_color(item_id, file_item.status)
                break
    
    def _update_item_color(self, item_id, status):
        """根据状态更新项颜色"""
        color_map = {
            FileStatus.SUCCESS: "success",
            FileStatus.FAILED: "danger", 
            FileStatus.PROCESSING: "warning",
            FileStatus.PENDING: "info",
            FileStatus.SKIPPED: "secondary"
        }
        
        if status in color_map:
            self.tree.set(item_id, "status", self.tree.set(item_id, "status"))
    
    def get_selected_items(self):
        """获取选中的文件项"""
        selected_ids = self.tree.selection()
        return [self.file_items[item_id] for item_id in selected_ids if item_id in self.file_items]
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 选择点击的项
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.tree.selection_set(item)
        
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def on_double_click(self, event):
        """双击事件 - 打开文件路径"""
        selected_items = self.get_selected_items()
        if selected_items:
            import subprocess
            import platform
            
            file_path = selected_items[0].path
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", "/select,", str(file_path)])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", "-R", str(file_path)])
                else:  # Linux
                    subprocess.run(["xdg-open", str(file_path.parent)])
            except Exception as e:
                self.main_app.log_panel.log(f"打开文件位置失败: {e}", "ERROR")
    
    def scan_selected(self):
        """扫描选中文件的备份"""
        selected_items = self.get_selected_items()
        if not selected_items:
            self.main_app.log_panel.log("请先选择要扫描的文件", "WARNING")
            return
        
        self.main_app.log_panel.log(f"开始扫描 {len(selected_items)} 个文件的备份...", "INFO")
        
        for item in selected_items:
            try:
                found_backup = self.main_app.backup_finder.find_nearest_backup(item.path)
                if found_backup:
                    item.message = f"找到备份: {found_backup.name}"
                    self.main_app.log_panel.log(f"✓ {item.name} 找到备份: {found_backup}", "SUCCESS")
                else:
                    item.message = "未找到备份文件"
                    self.main_app.log_panel.log(f"⚠ {item.name} 未找到备份", "WARNING")
                
                self.update_file_item(item)
                
            except Exception as e:
                item.message = f"扫描失败: {e}"
                self.main_app.log_panel.log(f"✗ {item.name} 扫描失败: {e}", "ERROR")
                self.update_file_item(item)
    
    def restore_selected(self):
        """恢复选中的文件"""
        selected_items = self.get_selected_items()
        if not selected_items:
            self.main_app.log_panel.log("请先选择要恢复的文件", "WARNING")
            return
        
        self.main_app.progress.start()
        self.main_app.log_panel.log(f"开始恢复 {len(selected_items)} 个文件...", "INFO")
        
        try:
            success_count = 0
            for item in selected_items:
                if item.status == FileStatus.SUCCESS:
                    self.main_app.log_panel.log(f"⏭️ {item.name} 已恢复，跳过", "INFO")
                    continue
                
                item.status = FileStatus.PROCESSING
                self.update_file_item(item)
                
                result = self.main_app._process_single_file(item)
                self.update_file_item(item)
                
                if result['status'] == 'success':
                    success_count += 1
            
            self.main_app.log_panel.log(f"恢复完成！成功: {success_count}/{len(selected_items)}", "SUCCESS")
            
        finally:
            self.main_app.progress.stop()
    
    def remove_selected(self):
        """移除选中的项"""
        selected_ids = self.tree.selection()
        if not selected_ids:
            self.main_app.log_panel.log("请先选择要移除的文件", "WARNING")
            return
        
        # 从队列中移除
        for item_id in selected_ids:
            if item_id in self.file_items:
                file_item = self.file_items[item_id]
                # 从文件管理器队列中移除
                self.main_app.file_manager.file_queue.remove_item(file_item.id)
                # 从本地映射中移除
                del self.file_items[item_id]
                # 从树视图中移除
                self.tree.delete(item_id)
        
        self.main_app.log_panel.log(f"已移除 {len(selected_ids)} 个文件", "INFO")
    
    def clear_queue(self):
        """清空队列"""
        # 清空树视图
        self.tree.delete(*self.tree.get_children())
        # 清空映射
        self.file_items.clear()
        # 清空文件管理器队列
        self.main_app.file_manager.file_queue.clear()
        
        self.main_app.log_panel.log("队列已清空", "INFO")
    
    def on_drop(self, event):
        """拖拽文件处理"""
        files = self.master.tk.splitlist(event.data)
        self.main_app.add_files_to_queue(files)
        
        if not self.main_app.auto_mode.get():
            self.main_app.log_panel.log(f"已添加 {len(files)} 个文件到队列，请手动操作", "INFO")