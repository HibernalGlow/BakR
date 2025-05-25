"""
BakR - 现代化TUI应用
参考Bagels架构设计的智能备份文件恢复工具
"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Optional, List
import argparse
from dataclasses import dataclass

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import (
    Button, Header, Footer, Static, Label, 
    Input, DataTable, Tree, DirectoryTree,
    Tabs, Tab, TabbedContent, TabPane,
    ProgressBar, Log, RichLog
)
from textual.screen import ModalScreen, Screen
from textual.binding import Binding
from textual.reactive import reactive, var
from textual.message import Message
from textual.events import Mount
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.syntax import Syntax
from rich import box

# 导入核心功能模块
from backup_finder import BackupFinder
from backup_restorer import BackupRestorer


@dataclass
class FileInfo:
    """文件信息数据类"""
    path: Path
    size: int
    exists: bool
    is_file: bool


@dataclass
class BackupInfo:
    """备份信息数据类"""
    path: Path
    size: int
    timestamp: float
    similarity: float


class BakRApp(App):
    """BakR主应用类"""
    
    CSS_PATH = "styles.tcss"
    TITLE = "BakR - 智能备份文件恢复工具"
    SUB_TITLE = "Intelligent Backup File Recovery Tool"
    
    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("r", "refresh", "刷新"),
        Binding("ctrl+o", "open_file", "打开文件"),
        Binding("ctrl+s", "save_settings", "保存设置"),
        Binding("f1", "help", "帮助"),
        Binding("f5", "scan_backups", "扫描备份"),
        Binding("escape", "clear_selection", "清除选择"),
    ]
    
    # 响应式变量
    current_file: reactive[Optional[Path]] = reactive(None)
    current_backup: reactive[Optional[Path]] = reactive(None)
    scan_progress: reactive[int] = reactive(0)
    status_message: reactive[str] = reactive("就绪")
    
    def __init__(self, files: Optional[List[Path]] = None):
        super().__init__()
        self.backup_finder = BackupFinder()
        self.backup_restorer = BackupRestorer()
        self.initial_files = files or []
        self.console = Console()
        
    def compose(self) -> ComposeResult:
        """组合界面组件"""
        yield Header(show_clock=True)
        
        with TabbedContent(initial="main"):
            with TabPane("主界面", id="main"):
                yield from self._compose_main_screen()
            
            with TabPane("文件浏览器", id="browser"):
                yield from self._compose_file_browser()
            
            with TabPane("设置", id="settings"):
                yield from self._compose_settings()
        
        yield Footer()
        
    def _compose_main_screen(self) -> ComposeResult:
        """组合主界面"""
        with Horizontal():
            # 左侧面板
            with Vertical(classes="left-panel"):
                yield Static("📁 选择的文件", classes="panel-title")
                yield Container(
                    Label("拖拽文件到此处或使用 Ctrl+O 打开", id="file-drop-zone"),
                    classes="drop-zone"
                )
                yield Static("", id="file-info", classes="info-panel")
                
                yield Static("⚙️ 快速操作", classes="panel-title")
                with Horizontal(classes="button-group"):
                    yield Button("选择文件", id="btn-select-file", variant="primary")
                    yield Button("清除", id="btn-clear", variant="default")
                
            # 右侧面板
            with Vertical(classes="right-panel"):
                yield Static("💾 备份文件", classes="panel-title")
                yield DataTable(id="backup-table", classes="backup-table")
                
                yield Static("📊 操作状态", classes="panel-title")
                yield Container(
                    Label(self.status_message, id="status-label"),
                    ProgressBar(id="progress-bar", show_eta=False),
                    classes="status-panel"
                )
                
                with Horizontal(classes="button-group"):
                    yield Button("扫描备份", id="btn-scan", variant="success")
                    yield Button("恢复文件", id="btn-restore", variant="warning", disabled=True)
                
        # 底部日志区域
        yield Static("📋 操作日志", classes="panel-title")
        yield RichLog(id="log", classes="log-panel", max_lines=100)
        
    def _compose_file_browser(self) -> ComposeResult:
        """组合文件浏览器"""
        with Horizontal():
            yield DirectoryTree("./", id="dir-tree", classes="file-browser")
            with Vertical():
                yield Static("文件预览", classes="panel-title")
                yield Static("", id="file-preview", classes="preview-panel")
                
    def _compose_settings(self) -> ComposeResult:
        """组合设置界面"""
        with Vertical():
            yield Static("⚙️ 设置选项", classes="panel-title")
            with Grid(classes="settings-grid"):
                yield Label("备份扫描目录:")
                yield Input(placeholder="输入备份目录路径", id="backup-dir")
                yield Label("文件扩展名过滤:")
                yield Input(placeholder="例如: .bak,.backup", id="extensions")
                yield Label("最大扫描深度:")
                yield Input(placeholder="默认: 5", id="max-depth")
                
            with Horizontal(classes="button-group"):
                yield Button("保存设置", id="btn-save-settings", variant="primary")
                yield Button("重置", id="btn-reset-settings", variant="default")
    
    def on_mount(self) -> None:
        """应用挂载时的初始化"""
        self.log_message("BakR 启动完成", "success")
        
        # 如果有初始文件，处理它们
        if self.initial_files:
            for file_path in self.initial_files:
                if file_path.exists():
                    self.handle_file_selection(file_path)
                    break
        
        # 设置备份表格列
        table = self.query_one("#backup-table", DataTable)
        table.add_columns("备份文件", "大小", "修改时间", "相似度")
        
    def log_message(self, message: str, level: str = "info") -> None:
        """记录日志消息"""
        log = self.query_one("#log", RichLog)
        
        if level == "success":
            styled_msg = Text(f"✅ {message}", style="green")
        elif level == "error":
            styled_msg = Text(f"❌ {message}", style="red")
        elif level == "warning":
            styled_msg = Text(f"⚠️ {message}", style="yellow")
        else:
            styled_msg = Text(f"ℹ️ {message}", style="blue")
            
        log.write(styled_msg)
        
    def update_status(self, message: str, progress: Optional[int] = None) -> None:
        """更新状态信息"""
        self.status_message = message
        status_label = self.query_one("#status-label", Label)
        status_label.update(message)
        
        if progress is not None:
            progress_bar = self.query_one("#progress-bar", ProgressBar)
            progress_bar.update(progress=progress)
    
    @on(Button.Pressed, "#btn-select-file")
    async def on_select_file(self) -> None:
        """选择文件按钮事件"""
        try:
            # 使用tkinter文件对话框
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            file_path = filedialog.askopenfilename(
                title="选择要恢复的文件",
                filetypes=[
                    ("所有文件", "*.*"),
                    ("文本文件", "*.txt"),
                    ("文档文件", "*.doc;*.docx"),
                    ("图片文件", "*.jpg;*.png;*.gif"),
                ]
            )
            
            if file_path:
                await self.handle_file_selection(Path(file_path))
                
        except Exception as ex:
            self.log_message(f"文件选择失败: {ex}", "error")
    
    @on(Button.Pressed, "#btn-clear")
    async def on_clear_selection(self) -> None:
        """清除选择"""
        self.current_file = None
        self.current_backup = None
        
        # 清除界面
        file_info = self.query_one("#file-info", Static)
        file_info.update("")
        
        table = self.query_one("#backup-table", DataTable)
        table.clear()
        
        # 禁用恢复按钮
        restore_btn = self.query_one("#btn-restore", Button)
        restore_btn.disabled = True
        
        self.update_status("已清除选择")
        self.log_message("已清除所有选择")
    
    @on(Button.Pressed, "#btn-scan")
    async def on_scan_backups(self) -> None:
        """扫描备份文件"""
        if not self.current_file:
            self.log_message("请先选择文件", "warning")
            return
            
        await self.scan_backup_files()
    
    @on(Button.Pressed, "#btn-restore")
    async def on_restore_file(self) -> None:
        """恢复文件"""
        if not self.current_file or not self.current_backup:
            self.log_message("请先选择文件和备份", "warning")
            return
            
        # 显示确认对话框
        if await self.show_restore_confirmation():
            await self.restore_file()
    
    async def handle_file_selection(self, file_path: Path) -> None:
        """处理文件选择"""
        try:
            self.current_file = file_path
            self.log_message(f"选择文件: {file_path}")
            
            # 更新文件信息显示
            self.update_file_info(file_path)
            
            # 自动扫描备份
            await self.scan_backup_files()
            
        except Exception as ex:
            self.log_message(f"处理文件失败: {ex}", "error")
    
    def update_file_info(self, file_path: Path) -> None:
        """更新文件信息显示"""
        try:
            file_info = self.query_one("#file-info", Static)
            
            if file_path.exists():
                size = file_path.stat().st_size
                size_str = self.format_file_size(size)
                
                info_panel = Panel(
                    f"[bold]文件名:[/bold] {file_path.name}\n"
                    f"[bold]大小:[/bold] {size_str}\n"
                    f"[bold]路径:[/bold] {file_path}\n"
                    f"[bold]状态:[/bold] [green]存在[/green]",
                    title="文件信息",
                    border_style="blue"
                )
            else:
                info_panel = Panel(
                    f"[bold]文件名:[/bold] {file_path.name}\n"
                    f"[bold]路径:[/bold] {file_path}\n"
                    f"[bold]状态:[/bold] [red]不存在[/red]",
                    title="文件信息",
                    border_style="red"
                )
            
            file_info.update(info_panel)
            
        except Exception as ex:
            self.log_message(f"更新文件信息失败: {ex}", "error")
    
    async def scan_backup_files(self) -> None:
        """扫描备份文件"""
        if not self.current_file:
            return
            
        try:
            self.update_status("正在扫描备份文件...", 0)
            self.log_message("开始扫描备份文件...")
            
            # 使用后台任务扫描
            backup_files = await self.run_backup_scan()
            
            # 更新备份表格
            table = self.query_one("#backup-table", DataTable)
            table.clear()
            if backup_files:
                for backup in backup_files:
                    size_str = self.format_file_size(backup['size'])
                    # 处理时间戳转换
                    import datetime
                    if isinstance(backup['timestamp'], (int, float)):
                        time_str = datetime.datetime.fromtimestamp(backup['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        time_str = str(backup['timestamp'])
                    similarity = f"{backup['similarity']:.1%}"
                    
                    table.add_row(
                        backup['path'].name,
                        size_str,
                        time_str,
                        similarity,
                        key=str(backup['path'])
                    )
                
                self.log_message(f"找到 {len(backup_files)} 个备份文件", "success")
                
                # 启用恢复按钮
                restore_btn = self.query_one("#btn-restore", Button)
                restore_btn.disabled = False
            else:
                self.log_message("未找到备份文件", "warning")
                
            self.update_status("扫描完成", 100)
            
        except Exception as ex:
            self.log_message(f"扫描备份失败: {ex}", "error")
            self.update_status("扫描失败")
    
    async def run_backup_scan(self) -> List[dict]:
        """在后台运行备份扫描"""
        def scan_sync():
            if not self.current_file:
                return []
                
            backup = self.backup_finder.find_nearest_backup(str(self.current_file))
            if backup and backup.get('success') and backup.get('backup_path'):
                backup_path = Path(backup['backup_path'])
                if backup_path.exists():
                    return [{
                        'path': backup_path,
                        'size': backup_path.stat().st_size,
                        'timestamp': backup.get('timestamp', backup_path.stat().st_mtime),
                        'similarity': backup.get('similarity', 1.0)
                    }]
            return []
        
        # 在线程池中运行同步扫描
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(scan_sync)
            return future.result()
    
    async def show_restore_confirmation(self) -> bool:
        """显示恢复确认对话框"""
        # 这里应该实现一个模态对话框
        # 为简化，暂时返回True
        return True
    
    async def restore_file(self) -> None:
        """执行文件恢复"""
        try:
            if not self.current_file or not self.current_backup:
                return
                
            self.update_status("正在恢复文件...", 0)
            self.log_message("开始恢复文件...")
            
            # 在后台执行恢复
            success = await self.run_restore_operation()
            
            if success:
                self.log_message("文件恢复成功！", "success")
                self.update_status("恢复完成", 100)
            else:
                self.log_message("文件恢复失败", "error")
                self.update_status("恢复失败")
                
        except Exception as ex:
            self.log_message(f"恢复过程中发生错误: {ex}", "error")
            self.update_status("恢复失败")
    
    async def run_restore_operation(self) -> bool:
        """在后台运行恢复操作"""
        def restore_sync():
            try:
                result = self.backup_restorer.restore_backup(
                    self.current_file, self.current_backup
                )
                return result.get('success', False)
            except Exception:
                return False
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(restore_sync)
            return future.result()
    
    @on(DataTable.RowSelected, "#backup-table")
    def on_backup_selected(self, event: DataTable.RowSelected) -> None:
        """备份文件选择事件"""
        table = event.data_table
        row_key = event.row_key
        
        if row_key:
            self.current_backup = Path(row_key)
            self.log_message(f"选择备份文件: {self.current_backup.name}")
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        import math
        
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    # 快捷键操作
    def action_quit(self) -> None:
        """退出应用"""
        self.exit()
    
    def action_refresh(self) -> None:
        """刷新"""
        self.log_message("刷新界面")
    
    async def action_open_file(self) -> None:
        """打开文件"""
        await self.on_select_file()
    
    def action_clear_selection(self) -> None:
        """清除选择"""
        self.run_worker(self.on_clear_selection, exclusive=True)
    
    async def action_scan_backups(self) -> None:
        """扫描备份"""
        await self.scan_backup_files()


def main():
    """主函数 - 处理命令行参数"""
    parser = argparse.ArgumentParser(
        description="BakR - 智能备份文件恢复工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python run_tui.py                    # 启动TUI界面
  python run_tui.py file1.txt          # 直接打开文件
  python run_tui.py file1.txt file2.py # 处理多个文件
  
拖拽文件到终端也可以直接启动！
        """
    )
    
    parser.add_argument(
        "files",
        nargs="*",
        help="要处理的文件路径（支持拖拽）"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    args = parser.parse_args()
    
    # 处理文件参数
    files = []
    if args.files:
        for file_arg in args.files:
            file_path = Path(file_arg).resolve()
            files.append(file_path)
    
    # 创建并运行应用
    app = BakRApp(files=files)
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n应用已退出")
    except Exception as ex:
        print(f"应用运行出错: {ex}")
        if args.debug:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
