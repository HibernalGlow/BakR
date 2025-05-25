"""
BakR - 命令行版本
支持交互式输入和批量处理的备份文件恢复工具
使用核心模块实现CLI兼容性
"""
import sys
import argparse
import math
from pathlib import Path
from typing import List, Optional
import time

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt, IntPrompt
from rich.text import Text
from rich.layout import Layout
from rich.live import Live

# 添加src目录到路径以支持核心模块导入
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from core.backup_finder import BackupFinder
from core.backup_restorer import BackupRestorer
from core.file_queue import FileQueue, FileQueueItem, FileStatus
from core.multi_file_manager import MultiFileManager


class BakRCLI:
    """BakR 命令行应用类"""
    
    def __init__(self):
        self.backup_finder = BackupFinder()
        self.backup_restorer = BackupRestorer()
        self.file_manager = MultiFileManager(self.backup_finder, self.backup_restorer)
        self.console = Console()
    
    def print_banner(self):
        """打印启动横幅"""
        banner = Panel.fit(
            "[bold blue]BakR v2.0[/bold blue] - 智能备份文件恢复工具\n"
            "[dim]支持交互式输入和批量处理[/dim]",
            border_style="blue"
        )
        self.console.print(banner)
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def show_interactive_menu(self):
        """显示交互式主菜单"""
        while True:
            self.console.print("\n[bold cyan]BakR 主菜单[/bold cyan]")
            self.console.print("1. 📁 添加文件到队列")
            self.console.print("2. 📋 查看文件队列")
            self.console.print("3. 🔍 扫描备份文件")
            self.console.print("4. 🔄 恢复文件")
            self.console.print("5. 🗑️  清空队列")
            self.console.print("6. 📊 显示统计信息")
            self.console.print("7. 💾 保存/加载队列")
            self.console.print("0. 🚪 退出")
            
            try:
                choice = IntPrompt.ask("\n[yellow]请选择操作[/yellow]", default=0)
            except KeyboardInterrupt:
                choice = 0
            
            if choice == 1:
                self.add_files_interactive()
            elif choice == 2:
                self.show_file_queue()
            elif choice == 3:
                self.scan_backups_interactive()
            elif choice == 4:
                self.restore_files_interactive()
            elif choice == 5:
                self.clear_queue()
            elif choice == 6:
                self.show_statistics()
            elif choice == 7:
                self.save_load_queue_menu()
            elif choice == 0:
                self.console.print("[yellow]感谢使用 BakR！[/yellow]")
                break
            else:
                self.console.print("[red]无效选择，请重试[/red]")
    
    def add_files_interactive(self):
        """交互式添加文件"""
        self.console.print("\n[bold]添加文件到队列[/bold]")
        self.console.print("[dim]提示: 可以输入文件路径或拖拽文件到终端[/dim]")
        
        while True:
            file_path = Prompt.ask(
                "[cyan]请输入文件路径[/cyan] (回车结束添加)",
                default=""
            )
            
            if not file_path.strip():
                break
                
            # 处理可能的引号和空格
            file_path = file_path.strip().strip('"').strip("'")
            path = Path(file_path)
            
            if not path.exists():
                self.console.print(f"[red]文件不存在: {file_path}[/red]")
                continue
            
            # 创建文件队列项
            file_item = FileQueueItem(
                id=f"{path.name}_{path.stat().st_size}_{int(time.time())}",
                name=path.name,
                path=path,
                size=path.stat().st_size,
                status=FileStatus.PENDING,
                message="已添加到队列"
            )
            
            # 添加到队列
            self.file_manager.file_queue.add_item(file_item)
            self.console.print(f"[green]✓ 已添加: {path.name}[/green]")
    
    def show_file_queue(self):
        """显示文件队列"""
        queue = self.file_manager.file_queue
        
        if not queue.items:
            self.console.print("\n[yellow]队列为空[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("文件名", style="cyan")
        table.add_column("大小", justify="right")
        table.add_column("状态", justify="center")
        table.add_column("消息", style="dim")
        
        for i, item in enumerate(queue.items, 1):
            status_color = {
                FileStatus.PENDING: "yellow",
                FileStatus.PROCESSING: "blue",
                FileStatus.COMPLETED: "green",
                FileStatus.ERROR: "red",
                FileStatus.CANCELLED: "dim"
            }.get(item.status, "white")
            
            table.add_row(
                str(i),
                item.name,
                self.format_file_size(item.size),
                f"[{status_color}]{item.status.value}[/{status_color}]",
                item.message
            )
        
        self.console.print(f"\n[bold]文件队列 ({len(queue.items)} 个文件):[/bold]")
        self.console.print(table)
    
    def scan_backups_interactive(self):
        """交互式扫描备份"""
        queue = self.file_manager.file_queue
        pending_items = [item for item in queue.items if item.status == FileStatus.PENDING]
        
        if not pending_items:
            self.console.print("\n[yellow]没有待处理的文件[/yellow]")
            return
        
        self.console.print(f"\n[bold]准备扫描 {len(pending_items)} 个文件的备份[/bold]")
        # if not Confirm.ask("确认开始扫描？"):
        #     return
        
        # 执行批量扫描
        def progress_callback(progress, message):
            percentage = int(progress * 100)
            self.console.print(f"[{percentage}%] {message}")
        
        # 设置进度回调并执行扫描
        self.file_manager.set_progress_callback(progress_callback)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("扫描备份文件...", total=None)
            success = self.file_manager.batch_scan_backups()
        if success:
            self.console.print("[green]✓ 扫描完成[/green]")
        else:
            self.console.print("[red]✗ 扫描失败[/red]")
    
    def restore_files_interactive(self):
        """交互式恢复文件"""
        queue = self.file_manager.file_queue
        restorable_items = [
            item for item in queue.items 
            if item.status == FileStatus.COMPLETED and item.backup_files
        ]
        
        if not restorable_items:
            self.console.print("\n[yellow]没有可恢复的文件[/yellow]")
            self.console.print("[dim]请先扫描备份文件[/dim]")
            return
        
        # 显示可恢复文件
        self.console.print(f"\n[bold]找到 {len(restorable_items)} 个可恢复文件:[/bold]")
        for i, item in enumerate(restorable_items, 1):
            self.console.print(f"{i}. {item.name} (1 个备份)")
        
        # 选择恢复方式
        self.console.print("\n[cyan]恢复选项:[/cyan]")
        self.console.print("1. 批量恢复所有文件（使用最佳匹配）")
        self.console.print("2. 单独选择文件恢复")
        self.console.print("0. 返回主菜单")
        
        choice = IntPrompt.ask("[yellow]请选择[/yellow]", default=0)
        
        if choice == 1:
            self.batch_restore_files()
        elif choice == 2:
            self.restore_single_file_interactive(restorable_items)
    
    def batch_restore_files(self):
        """批量恢复文件"""
        if not Confirm.ask("[bold red]这将覆盖原文件，确认批量恢复？[/bold red]"):
            return
        
        def progress_callback(progress, message):
            percentage = int(progress * 100)
            self.console.print(f"[{percentage}%] {message}")
        
        # 设置进度回调并执行恢复
        self.file_manager.set_progress_callback(progress_callback)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("恢复文件...", total=None)
            success = self.file_manager.batch_restore_files()
        
        if success:
            self.console.print("[green]✓ 批量恢复完成[/green]")
        else:
            self.console.print("[red]✗ 批量恢复失败[/red]")
    def restore_single_file_interactive(self, restorable_items):
        """单文件交互式恢复"""
        file_choice = IntPrompt.ask(
            f"[cyan]选择要恢复的文件[/cyan] (1-{len(restorable_items)})",
            default=1
        ) - 1
        
        if 0 <= file_choice < len(restorable_items):
            item = restorable_items[file_choice]
            
            # 显示备份信息
            self.console.print(f"\n[bold]{item.name} 的备份信息:[/bold]")
            if item.backup_files:
                backup = item.backup_files[0]  # 使用第一个备份
                
                self.console.print(f"备份文件: {backup.path}")
                self.console.print(f"相似度: {backup.similarity * 100:.1f}%")
                self.console.print(f"大小: {self.format_file_size(backup.size)}")
                
                # 确认恢复
                if Confirm.ask(f"[bold red]确认恢复 {item.name}？[/bold red]"):
                    # 设置选中的备份
                    item.set_selected_backup(backup.path)
                    success = self.file_manager.restore_file(item.id)
                    if success:
                        self.console.print("[green]✓ 恢复成功[/green]")
                    else:
                        self.console.print("[red]✗ 恢复失败[/red]")
            else:
                self.console.print("[red]没有可用的备份文件[/red]")
    
    def clear_queue(self):
        """清空队列"""
        if Confirm.ask("[yellow]确认清空文件队列？[/yellow]"):
            self.file_manager.file_queue.clear()
            self.console.print("[green]✓ 队列已清空[/green]")
    
    def show_statistics(self):
        """显示统计信息"""
        queue = self.file_manager.file_queue
        stats = queue.get_status_stats()
        
        table = Table(show_header=True, header_style="bold green")
        table.add_column("状态", style="cyan")
        table.add_column("数量", justify="right")
        table.add_column("百分比", justify="right")
        
        total = len(queue.items)
        for status, count in stats.items():
            percentage = (count / total * 100) if total > 0 else 0
            table.add_row(
                status.value,
                str(count),
                f"{percentage:.1f}%"
            )
        
        self.console.print(f"\n[bold]队列统计 (总计: {total} 个文件):[/bold]")
        self.console.print(table)
    
    def save_load_queue_menu(self):
        """保存/加载队列菜单"""
        self.console.print("\n[cyan]队列管理:[/cyan]")
        self.console.print("1. 💾 保存队列")
        self.console.print("2. 📂 加载队列") 
        self.console.print("0. 返回主菜单")
        
        choice = IntPrompt.ask("[yellow]请选择[/yellow]", default=0)
        
        if choice == 1:
            self.save_queue()
        elif choice == 2:
            self.load_queue()
    
    def save_queue(self):
        """保存队列"""
        filename = Prompt.ask(
            "[cyan]保存文件名[/cyan]", 
            default=f"bakr_queue_{int(time.time())}.json"
        )
        
        try:
            self.file_manager.file_queue.save_to_file(filename)
            self.console.print(f"[green]✓ 队列已保存到: {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]✗ 保存失败: {e}[/red]")
    
    def load_queue(self):
        """加载队列"""
        filename = Prompt.ask("[cyan]队列文件名[/cyan]")
        
        if not filename:
            return
            
        try:
            self.file_manager.file_queue.load_from_file(filename)
            self.console.print(f"[green]✓ 队列已加载: {len(self.file_manager.file_queue.items)} 个文件[/green]")
        except Exception as e:
            self.console.print(f"[red]✗ 加载失败: {e}[/red]")
    
    def run(self, file_paths: List[str], interactive: bool = False):
        """运行主程序"""
        self.print_banner()
        
        if interactive or not file_paths:
            # 交互式模式
            if file_paths:
                self.add_files_from_args(file_paths)
            self.show_interactive_menu()
        else:
            # 传统批处理模式
            self.run_batch_mode(file_paths)
    
    def add_files_from_args(self, file_paths: List[str]):
        """从命令行参数添加文件"""
        added_count = 0
        for path_str in file_paths:
            path = Path(path_str.strip('"').strip("'"))
            
            if not path.exists():
                self.console.print(f"[red]文件不存在: {path}[/red]")
                continue
            
            file_item = FileQueueItem(
                id=f"{path.name}_{path.stat().st_size}_{int(time.time())}_{added_count}",
                name=path.name,
                path=path,
                size=path.stat().st_size,
                status=FileStatus.PENDING,
                message="从命令行添加"
            )
            
            self.file_manager.file_queue.add_item(file_item)
            added_count += 1
        
        if added_count > 0:
            self.console.print(f"[green]✓ 已添加 {added_count} 个文件到队列[/green]")
    
    def run_batch_mode(self, file_paths: List[str]):
        """传统批处理模式"""
        # 添加文件到队列
        self.add_files_from_args(file_paths)
        
        if not self.file_manager.file_queue.items:
            self.console.print("[red]没有有效的文件可处理[/red]")
            return
        
        # 显示文件队列
        self.show_file_queue()
        
        # 扫描备份
        if Confirm.ask("\n[cyan]开始扫描备份文件？[/cyan]"):
            self.scan_backups_batch()
          # 恢复文件
        restorable_count = len([
            item for item in self.file_manager.file_queue.items
            if item.status == FileStatus.COMPLETED and item.backup_files
        ])
        
        if restorable_count > 0:
            if Confirm.ask(f"\n[cyan]找到 {restorable_count} 个可恢复文件，开始恢复？[/cyan]"):
                self.batch_restore_files()
        
        # 显示最终统计
        self.show_statistics()
    
    def scan_backups_batch(self):
        """批处理模式扫描备份"""
        def progress_callback(progress, message):
            percentage = int(progress * 100)
            self.console.print(f"[{percentage}%] {message}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("扫描备份文件...", total=None)
            self.file_manager.set_progress_callback(progress_callback)
            success = self.file_manager.batch_scan_backups()
        
        if success:
            self.console.print("[green]✓ 备份扫描完成[/green]")
        else:
            self.console.print("[red]✗ 备份扫描失败[/red]")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='BakR - 智能备份文件恢复工具')
    parser.add_argument('files', nargs='*', help='要处理的文件路径')
    parser.add_argument('-i', '--interactive', action='store_true', 
                        help='启动交互式模式')
    
    args = parser.parse_args()
    
    app = BakRCLI()
    app.run(args.files, args.interactive)


if __name__ == "__main__":
    main()
