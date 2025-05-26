import sys
import time
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt, IntPrompt
from rich.box import SIMPLE_HEAVY

from baku.core.backup_finder import BackupFinder
from baku.core.backup_restorer import BackupRestorer
from baku.core.file_queue import FileQueue, FileQueueItem, FileStatus
from baku.core.multi_file_manager import MultiFileManager

class RichPanelApp:
    """基于 rich 的 TUI 应用，数字菜单模式"""
    def __init__(self):
        self.console = Console()
        self.backup_finder = BackupFinder()
        self.backup_restorer = BackupRestorer()
        self.file_manager = MultiFileManager(self.backup_finder, self.backup_restorer)
        self.layout = Layout()
        self.input_buffer = ""
        self.message = "请输入数字选择操作"
        self.running = True
        self.last_table = None
        self.menu_items = [
            ("1", "添加文件到队列"),
            ("2", "恢复所有可恢复文件"),
            ("0", "退出")
        ]

    def format_file_size(self, size_bytes: int) -> str:
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int((size_bytes).bit_length() // 10) if size_bytes else 0
        p = 1024 ** i
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    def get_backup_table(self):
        restorable_items = self.file_manager.file_queue.get_restorable_items()
        table = Table(title="备份文件列表", box=SIMPLE_HEAVY, expand=True)
        table.add_column("原文件", style="cyan", no_wrap=True)
        table.add_column("备份文件", style="green")
        table.add_column("类型", style="magenta")
        table.add_column("目录", style="yellow")
        table.add_column("回溯层级", style="dim", justify="right")
        table.add_column("大小", style="white", justify="right")
        table.add_column("修改时间", style="white")
        for item in restorable_items:
            backup_path = item.selected_backup
            if not backup_path:
                continue
            try:
                orig_dir = item.path.parent.resolve()
                bak_dir = backup_path.parent.resolve()
                level = 0
                cur = orig_dir
                while cur != bak_dir and cur != cur.parent:
                    cur = cur.parent
                    level += 1
                bak_type = "同名" if (item.path.stem == backup_path.stem or item.path.name in backup_path.name) and level == 0 else "回溯"
            except Exception:
                bak_type = "?"
                level = "?"
            try:
                size = backup_path.stat().st_size
                mtime = backup_path.stat().st_mtime
                import datetime
                mtime_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                size = "?"
                mtime_str = "?"
            table.add_row(
                item.name,
                str(backup_path),
                bak_type,
                str(backup_path.parent),
                str(level),
                self.format_file_size(size) if isinstance(size, int) else size,
                mtime_str            )
        return table

    def refresh_table(self):
        self.last_table = self.get_backup_table()

    def parse_file_path(self, file_path: str) -> str:
        """解析文件路径，处理 PowerShell 拖拽格式和引号"""
        path_str = file_path.strip()
        
        # 处理 PowerShell 拖拽格式：& 'path with spaces'
        if path_str.startswith("& "):
            path_str = path_str[2:].strip()
        
        # 移除外层引号
        if (path_str.startswith('"') and path_str.endswith('"')) or \
           (path_str.startswith("'") and path_str.endswith("'")):
            path_str = path_str[1:-1]
        
        return path_str

    def add_file_and_scan(self, file_path: str):
        """添加单个文件并扫描"""
        parsed_path = self.parse_file_path(file_path)
        path = Path(parsed_path)
        
        if not path.exists():
            self.message = f"[red]文件不存在: {file_path}[/red]"
            return False
            
        file_item = FileQueueItem(
            id=f"{path.name}_{path.stat().st_size}_{int(time.time())}",
            name=path.name,
            path=path,
            size=path.stat().st_size,
            status=FileStatus.PENDING,
            message="已添加到队列"
        )
        self.file_manager.file_queue.add_item(file_item)
        self.console.print(f"[green]✓ 已添加: {path.name}[/green]")
        return True

    def add_files_interactive(self):
        """交互式添加多个文件"""
        self.console.clear()
        self.console.print("[bold]添加文件到队列[/bold]")
        self.console.print("[dim]提示: 可以输入文件路径或拖拽文件到终端[/dim]")
        self.console.print("[dim]支持 PowerShell 拖拽格式: & 'path with spaces'[/dim]")
        self.console.print("[dim]输入空行结束添加[/dim]\n")
        
        added_count = 0
        while True:
            file_path = Prompt.ask(
                "[cyan]请输入文件路径[/cyan]",
                default=""
            )
            
            if not file_path.strip():
                break
                
            if self.add_file_and_scan(file_path):
                added_count += 1
        
        if added_count > 0:
            # 批量扫描所有添加的文件
            self.console.print(f"\n[yellow]开始扫描 {added_count} 个文件的备份...[/yellow]")
            self.file_manager.batch_scan_backups()
            self.message = f"[green]已添加并扫描 {added_count} 个文件[/green]"
            self.refresh_table()
        else:
            self.message = "[yellow]未添加任何文件[/yellow]"

    def restore_all(self):
        from baku.config.config import config_info
        success = self.file_manager.batch_restore_files()
        if success:
            self.message = "[green]批量恢复完成[/green]"
        else:
            self.message = f"[red]批量恢复失败，日志见: {config_info['log_file']}[/red]"
        self.refresh_table()

    def handle_menu(self, choice: str):
        if choice == "1":
            self.add_files_interactive()
        elif choice == "2":
            self.restore_all()
        elif choice == "0":
            self.running = False
        else:
            self.message = "[yellow]无效选择，请输入菜单数字[/yellow]"

    def make_layout(self):
        layout = Layout()
        layout.split(
            Layout(name="main", ratio=8),
            Layout(name="footer", size=6)
        )
        # 主区
        main_panel = Panel(self.last_table or Text("暂无数据，先添加文件"), title="baku 备份恢复", border_style="blue")
        layout["main"].update(main_panel)
        # 底部菜单区
        menu_text = "\n".join([f"{num}. {desc}" for num, desc in self.menu_items])
        footer_panel = Panel(
            Align.left(f"菜单：\n{menu_text}\n\n{self.message}", vertical="middle"),
            border_style="magenta"
        )
        layout["footer"].update(footer_panel)
        return layout    
    def run(self):
        self.refresh_table()
        
        while self.running:
            try:
                # 显示当前状态
                self.console.clear()
                self.console.print(self.make_layout())
                
                # 获取用户输入
                choice = Prompt.ask("请输入菜单数字")
                self.input_buffer = choice
                self.handle_menu(choice.strip())
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                self.message = f"[red]错误: {e}[/red]"

if __name__ == "__main__":
    app = RichPanelApp()
    app.run() 