"""
BakR - 命令行版本
支持拖拽多个文件的备份文件恢复工具
"""
import sys
import argparse
from pathlib import Path
from typing import List, Optional
import time

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from backup_finder import BackupFinder
from backup_restorer import BackupRestorer


class BakRCLI:
    """BakR 命令行应用类"""
    
    def __init__(self):
        self.backup_finder = BackupFinder()
        self.backup_restorer = BackupRestorer()
        self.console = Console() if RICH_AVAILABLE else None
        
    def print_banner(self):
        """打印启动横幅"""
        if RICH_AVAILABLE:
            banner = Panel.fit(
                "[bold blue]BakR[/bold blue] - 智能备份文件恢复工具\n"
                "[dim]支持拖拽多个文件进行批量处理[/dim]",
                border_style="blue"
            )
            self.console.print(banner)
        else:
            print("=" * 50)
            print("BakR - 智能备份文件恢复工具")
            print("支持拖拽多个文件进行批量处理")
            print("=" * 50)
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def create_file_table(self, files: List[Path]) -> Table:
        """创建文件信息表格"""
        if not RICH_AVAILABLE:
            return None
            
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("文件名", style="cyan")
        table.add_column("大小", justify="right")
        table.add_column("路径", style="dim")
        table.add_column("状态", justify="center")
        
        for i, file_path in enumerate(files, 1):
            if file_path.exists():
                size = self.format_file_size(file_path.stat().st_size)
                status = "[green]✓ 存在[/green]"
            else:
                size = "N/A"
                status = "[red]✗ 不存在[/red]"
                
            table.add_row(
                str(i),
                file_path.name,
                size,
                str(file_path.parent),
                status
            )
        
        return table
    
    def search_backups_for_files(self, files: List[Path]) -> dict:
        """为多个文件搜索备份"""
        results = {}
        
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("搜索备份文件...", total=len(files))
                
                for file_path in files:
                    progress.update(task, description=f"搜索 {file_path.name}")
                    backup_path = self.backup_finder.find_nearest_backup(str(file_path))
                    results[file_path] = Path(backup_path) if backup_path else None
                    progress.advance(task)
        else:
            print("搜索备份文件...")
            for i, file_path in enumerate(files, 1):
                print(f"[{i}/{len(files)}] 搜索 {file_path.name}")
                backup_path = self.backup_finder.find_nearest_backup(str(file_path))
                results[file_path] = Path(backup_path) if backup_path else None
        
        return results
    
    def create_backup_table(self, backup_results: dict) -> Table:
        """创建备份文件信息表格"""
        if not RICH_AVAILABLE:
            return None
            
        table = Table(show_header=True, header_style="bold green")
        table.add_column("#", style="dim", width=3)
        table.add_column("原文件", style="cyan")
        table.add_column("备份文件", style="yellow")
        table.add_column("备份大小", justify="right")
        table.add_column("状态", justify="center")
        
        for i, (original, backup) in enumerate(backup_results.items(), 1):
            if backup and backup.exists():
                backup_size = self.format_file_size(backup.stat().st_size)
                status = "[green]✓ 找到[/green]"
                backup_name = backup.name
            else:
                backup_size = "N/A"
                status = "[red]✗ 未找到[/red]"
                backup_name = "无备份文件"
                
            table.add_row(
                str(i),
                original.name,
                backup_name,
                backup_size,
                status
            )
        
        return table
    
    def print_simple_results(self, files: List[Path], backup_results: dict):
        """简单模式打印结果（无rich时使用）"""
        print(f"\n找到 {len(files)} 个文件:")
        for i, file_path in enumerate(files, 1):
            print(f"{i}. {file_path.name}")
            if file_path.exists():
                size = self.format_file_size(file_path.stat().st_size)
                print(f"   大小: {size}")
            else:
                print(f"   状态: 文件不存在")
        
        print(f"\n备份搜索结果:")
        for i, (original, backup) in enumerate(backup_results.items(), 1):
            print(f"{i}. {original.name}")
            if backup and backup.exists():
                size = self.format_file_size(backup.stat().st_size)
                print(f"   备份: {backup.name} ({size})")
            else:
                print(f"   备份: 未找到")
    
    def restore_files(self, backup_results: dict) -> dict:
        """恢复多个文件"""
        restore_results = {}
        available_backups = {k: v for k, v in backup_results.items() 
                           if v and v.exists()}
        
        if not available_backups:
            if RICH_AVAILABLE:
                self.console.print("[red]没有找到可恢复的备份文件[/red]")
            else:
                print("没有找到可恢复的备份文件")
            return restore_results
        
        # 显示将要恢复的文件
        if RICH_AVAILABLE:
            self.console.print(f"\n[yellow]准备恢复 {len(available_backups)} 个文件:[/yellow]")
            for original, backup in available_backups.items():
                self.console.print(f"  {original.name} ← {backup.name}")
        else:
            print(f"\n准备恢复 {len(available_backups)} 个文件:")
            for original, backup in available_backups.items():
                print(f"  {original.name} <- {backup.name}")
        
        # 确认操作
        if RICH_AVAILABLE:
            confirm = Confirm.ask("\n[bold red]这将覆盖原文件，确认继续？[/bold red]")
        else:
            confirm_input = input("\n这将覆盖原文件，确认继续？(y/N): ")
            confirm = confirm_input.lower() in ['y', 'yes', '是']
        
        if not confirm:
            if RICH_AVAILABLE:
                self.console.print("[yellow]操作已取消[/yellow]")
            else:
                print("操作已取消")
            return restore_results
        
        # 执行恢复
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("恢复文件...", total=len(available_backups))
                
                for original, backup in available_backups.items():
                    progress.update(task, description=f"恢复 {original.name}")
                    try:
                        result = self.backup_restorer.restore_backup(original, backup)
                        restore_results[original] = result["success"]
                    except Exception as e:
                        restore_results[original] = False
                        if RICH_AVAILABLE:
                            self.console.print(f"[red]恢复 {original.name} 失败: {e}[/red]")
                        else:
                            print(f"恢复 {original.name} 失败: {e}")
                    progress.advance(task)
        else:
            print("恢复文件...")
            for i, (original, backup) in enumerate(available_backups.items(), 1):
                print(f"[{i}/{len(available_backups)}] 恢复 {original.name}")
                try:
                    result = self.backup_restorer.restore_backup(original, backup)
                    restore_results[original] = result["success"]
                except Exception as e:
                    restore_results[original] = False
                    print(f"恢复 {original.name} 失败: {e}")
        
        return restore_results
    
    def print_restore_summary(self, restore_results: dict):
        """打印恢复结果摘要"""
        if not restore_results:
            return
            
        success_count = sum(restore_results.values())
        total_count = len(restore_results)
        
        if RICH_AVAILABLE:
            if success_count == total_count:
                self.console.print(f"\n[green]✓ 全部 {total_count} 个文件恢复成功！[/green]")
            else:
                self.console.print(f"\n[yellow]恢复完成: {success_count}/{total_count} 个文件成功[/yellow]")
                
            # 详细结果
            for file_path, success in restore_results.items():
                status = "[green]✓[/green]" if success else "[red]✗[/red]"
                self.console.print(f"  {status} {file_path.name}")
        else:
            print(f"\n恢复完成: {success_count}/{total_count} 个文件成功")
            for file_path, success in restore_results.items():
                status = "✓" if success else "✗"
                print(f"  {status} {file_path.name}")
    
    def run(self, file_paths: List[str]):
        """运行主程序"""
        self.print_banner()
        
        # 转换为Path对象并验证
        files = []
        for path_str in file_paths:
            path = Path(path_str.strip('"').strip("'"))  # 移除可能的引号
            files.append(path)
        
        if not files:
            if RICH_AVAILABLE:
                self.console.print("[red]请提供要处理的文件路径[/red]")
                self.console.print("[dim]提示: 可以直接拖拽文件到终端[/dim]")
            else:
                print("请提供要处理的文件路径")
                print("提示: 可以直接拖拽文件到终端")
            return
        
        # 显示文件信息
        if RICH_AVAILABLE:
            file_table = self.create_file_table(files)
            self.console.print(f"\n[bold]处理 {len(files)} 个文件:[/bold]")
            self.console.print(file_table)
        
        # 搜索备份文件
        backup_results = self.search_backups_for_files(files)
        
        # 显示备份搜索结果
        if RICH_AVAILABLE:
            backup_table = self.create_backup_table(backup_results)
            self.console.print(f"\n[bold]备份搜索结果:[/bold]")
            self.console.print(backup_table)
        else:
            self.print_simple_results(files, backup_results)
        
        # 执行恢复
        restore_results = self.restore_files(backup_results)
        
        # 显示结果摘要
        self.print_restore_summary(restore_results)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="BakR - 智能备份文件恢复工具",
        epilog="提示: 可以直接将文件拖拽到终端来使用"
    )
    parser.add_argument(
        'files', 
        nargs='*', 
        help='要处理的文件路径（支持多个文件）'
    )
    parser.add_argument(
        '--install-rich', 
        action='store_true',
        help='安装 rich 库以获得更好的显示效果'
    )
    
    args = parser.parse_args()
    
    # 检查是否需要安装rich
    if args.install_rich:
        print("正在安装 rich 库...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
            print("rich 库安装成功！请重新运行程序。")
        except subprocess.CalledProcessError:
            print("安装失败，请手动运行: pip install rich")
        return
    
    # 如果没有提供文件参数，提示用户
    if not args.files:
        if RICH_AVAILABLE:
            console = Console()
            console.print("[yellow]BakR - 智能备份文件恢复工具[/yellow]")
            console.print("\n使用方法:")
            console.print("1. 直接拖拽文件到终端:")
            console.print("   [dim]python -m src.cli_app file1.txt file2.txt[/dim]")
            console.print("2. 或者手动输入文件路径:")
            console.print("   [dim]python -m src.cli_app \"C:\\path\\to\\file.txt\"[/dim]")
            console.print("\n[dim]提示: 如果显示效果不佳，运行 --install-rich 安装增强显示[/dim]")
        else:
            print("BakR - 智能备份文件恢复工具")
            print("\n使用方法:")
            print("1. 直接拖拽文件到终端:")
            print("   python -m src.cli_app file1.txt file2.txt")
            print("2. 或者手动输入文件路径:")
            print("   python -m src.cli_app \"C:\\path\\to\\file.txt\"")
            print("\n提示: 运行 --install-rich 安装 rich 库获得更好的显示效果")
        return
    
    # 创建应用并运行
    app = BakRCLI()
    app.run(args.files)


if __name__ == '__main__':
    main()
