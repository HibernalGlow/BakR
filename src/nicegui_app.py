"""
BakR - NiceGUI 版本
现代化的备份文件恢复工具界面
"""
import os
import asyncio
from pathlib import Path
from typing import Optional
import tempfile

from nicegui import ui, app, events
from backup_finder import BackupFinder
from backup_restorer import BackupRestorer


class BakRApp:
    """BakR NiceGUI 应用主类"""
    
    def __init__(self):
        self.backup_finder = BackupFinder()
        self.backup_restorer = BackupRestorer()
        self.current_file: Optional[Path] = None
        self.current_backup: Optional[Path] = None
        
        # UI 组件引用
        self.file_input = None
        self.status_card = None
        self.file_info_card = None
        self.backup_info_card = None
        self.restore_button = None
        self.log_area = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 设置页面标题和图标
        ui.page_title('BakR - 智能备份文件恢复工具')
        
        # 自定义CSS样式
        ui.add_head_html('''
        <style>
            .drop-zone {
                border: 2px dashed #ccc;
                border-radius: 10px;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .drop-zone:hover {
                border-color: #2196F3;
                background-color: #f5f5f5;
            }
            .drop-zone.dragover {
                border-color: #2196F3;
                background-color: #e3f2fd;
            }
            .file-card {
                border-left: 4px solid #2196F3;
            }
            .backup-card {
                border-left: 4px solid #4CAF50;
            }
            .status-card {
                border-left: 4px solid #FF9800;
            }
            .log-area {
                max-height: 200px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
            }
        </style>
        ''')
        
        # 主标题
        with ui.row().classes('w-full justify-center'):
            ui.label('BakR - 智能备份文件恢复工具').classes('text-3xl font-bold text-primary')
        
        ui.separator().classes('my-4')
          # 文件选择区域
        self.create_file_upload_zone()
        
        # 状态卡片区域
        with ui.row().classes('w-full gap-4'):
            self.create_file_info_card()
            self.create_backup_info_card()
            self.create_status_card()
        
        # 操作按钮区域
        with ui.row().classes('w-full justify-center gap-4 mt-4'):
            self.restore_button = ui.button(
                '恢复文件', 
                icon='restore',
                on_click=self.restore_file
            ).classes('bg-green-500 text-white').props('disabled')
            ui.button(
                '清除选择', 
                icon='clear',
                on_click=self.clear_selection
            ).classes('bg-gray-500 text-white')
        
        # 日志区域
        self.create_log_area()
    
    def create_file_upload_zone(self):
        """创建文件选择区域（支持拖拽和点击选择）"""
        with ui.card().classes('w-full drop-zone p-6'):
            with ui.column().classes('w-full items-center gap-4'):
                ui.icon('folder_open').classes('text-6xl text-gray-400')
                ui.label('拖拽文件到此处或点击选择').classes('text-lg text-gray-600')
                ui.label('支持所有文件类型').classes('text-sm text-gray-400')
                
                # 本地文件选择按钮
                ui.button(
                    '选择本地文件',
                    icon='file_open',
                    on_click=self.select_file
                ).classes('bg-blue-500 text-white text-lg px-6 py-2 mr-2')
                
                # 拖拽上传组件（用于演示文件内容）
                upload = ui.upload(
                    label='或拖拽文件到此处',
                    on_upload=self.handle_upload,
                    auto_upload=True
                ).classes('bg-green-500 text-white text-lg px-6 py-2').props('accept="*"')
                
                # 显示当前选择的文件路径
                self.selected_file_label = ui.label('未选择文件').classes('text-sm text-gray-500 mt-2')
    
    def create_file_info_card(self):
        """创建文件信息卡片"""
        with ui.card().classes('flex-1 file-card'):
            ui.card_section().classes('bg-blue-50')
            with ui.card_section():
                ui.label('📁 选中文件').classes('text-lg font-bold')
                self.file_info_card = ui.column().classes('gap-2')
                with self.file_info_card:
                    ui.label('暂无文件选择').classes('text-gray-500')
    
    def create_backup_info_card(self):
        """创建备份信息卡片"""
        with ui.card().classes('flex-1 backup-card'):
            ui.card_section().classes('bg-green-50')
            with ui.card_section():
                ui.label('💾 备份文件').classes('text-lg font-bold')
                self.backup_info_card = ui.column().classes('gap-2')
                with self.backup_info_card:
                    ui.label('暂无备份文件').classes('text-gray-500')
    
    def create_status_card(self):
        """创建状态卡片"""
        with ui.card().classes('flex-1 status-card'):
            ui.card_section().classes('bg-orange-50')
            with ui.card_section():
                ui.label('⚡ 操作状态').classes('text-lg font-bold')
                self.status_card = ui.column().classes('gap-2')
                with self.status_card:
                    ui.label('等待文件选择...').classes('text-gray-500')
    
    def create_log_area(self):
        """创建日志区域"""
        ui.separator().classes('my-4')
        with ui.card().classes('w-full'):
            with ui.card_section():
                ui.label('📋 操作日志').classes('text-lg font-bold')
                self.log_area = ui.log().classes('log-area w-full h-48')
                self.log('系统启动完成，等待文件选择...')
    
    def log(self, message: str, level: str = 'info'):
        """添加日志信息"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        icon = icons.get(level, 'ℹ️')
        formatted_message = f"[{timestamp}] {icon} {message}"
        self.log_area.push(formatted_message)
    
    def select_file(self):
        """选择本地文件"""
        try:
            # 使用tkinter文件对话框选择文件
            import tkinter as tk
            from tkinter import filedialog
            
            # 创建隐藏的根窗口
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择要恢复的文件",
                filetypes=[
                    ("所有文件", "*.*"),
                    ("文本文件", "*.txt"),
                    ("配置文件", "*.conf;*.cfg;*.ini"),
                    ("代码文件", "*.py;*.js;*.html;*.css")
                ]
            )
            
            root.destroy()
            if file_path:
                # 异步调用文件处理
                asyncio.create_task(self.handle_file_selection(file_path))
            
        except ImportError:
            ui.notify('需要安装 tkinter 库来支持文件选择', type='warning')
        except Exception as ex:
            self.log(f'文件选择失败: {str(ex)}', 'error')
            ui.notify(f'文件选择失败: {str(ex)}', type='negative')
    
    async def handle_file_selection(self, file_path: str):
        """处理文件选择"""
        try:
            self.log(f'选择文件: {file_path}')
            
            self.current_file = Path(file_path)
            self.selected_file_label.text = f'已选择: {file_path}'
            self.log(f'文件已选择: {self.current_file.name}', 'success')
            
            # 更新文件信息显示
            self.update_file_info()
              # 搜索备份文件
            await self.search_backup()
            
        except Exception as ex:
            self.log(f'处理文件失败: {str(ex)}', 'error')
            ui.notify(f'处理文件失败: {str(ex)}', type='negative')
    
    def update_file_info(self):
        """更新文件信息显示"""
        if not self.current_file or not self.current_file.exists():
            return
        
        self.file_info_card.clear()
        with self.file_info_card:
            file_size = self.format_file_size(self.current_file.stat().st_size)
            ui.label(f'文件名: {self.current_file.name}').classes('font-semibold')
            ui.label(f'大小: {file_size}')
            ui.label(f'路径: {self.current_file}').classes('text-sm text-gray-600')
        
        # 更新状态
        self.status_card.clear()
        with self.status_card:
            ui.label('正在搜索备份文件...').classes('text-blue-600')
    
    async def search_backup(self):
        """搜索备份文件"""
        if not self.current_file:
            return
        
        try:
            self.log('开始搜索备份文件...')
              # 在后台线程中搜索备份
            backup_path = await asyncio.get_event_loop().run_in_executor(
                None, self.backup_finder.find_nearest_backup, self.current_file
            )
            
            if backup_path:
                self.current_backup = Path(backup_path)
                self.log(f'找到备份文件: {backup_path}', 'success')
                self.update_backup_info()
                self.update_status('备份文件已找到，可以开始恢复')
                self.restore_button.props('disabled=false')
                self.restore_button.update()
            else:
                self.log('未找到备份文件', 'warning')
                self.update_status('未找到匹配的备份文件')
                self.restore_button.props('disabled=true')
                self.restore_button.update()
                
        except Exception as ex:
            self.log(f'搜索备份文件时发生错误: {str(ex)}', 'error')
            self.update_status('搜索失败')
    
    def update_backup_info(self):
        """更新备份信息显示"""
        if not self.current_backup or not self.current_backup.exists():
            self.backup_info_card.clear()
            with self.backup_info_card:
                ui.label('未找到备份文件').classes('text-gray-500')
            return
        
        self.backup_info_card.clear()
        with self.backup_info_card:
            file_size = self.format_file_size(self.current_backup.stat().st_size)
            ui.label(f'文件名: {self.current_backup.name}').classes('font-semibold')
            ui.label(f'大小: {file_size}')
            ui.label(f'路径: {self.current_backup}').classes('text-sm text-gray-600')
    
    def update_status(self, message: str):
        """更新状态显示"""
        self.status_card.clear()
        with self.status_card:
            ui.label(message)
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _restore_file_sync(self, backup_path: str, target_path: str) -> bool:
        """同步执行文件恢复"""
        try:
            result = self.backup_restorer.restore_backup(
                Path(target_path), Path(backup_path)
            )
            return result["success"]
        except Exception:
            return False
    
    async def restore_file(self):
        """恢复文件"""
        if not self.current_file or not self.current_backup:
            ui.notify('请先选择文件', type='warning')
            return
          # 显示确认对话框
        result = await self.show_confirm_dialog()
        if not result:
            return
        
        try:
            self.log('开始恢复文件...')
            self.update_status('正在恢复文件...')
            
            # 在后台线程中执行恢复操作
            success = await asyncio.get_event_loop().run_in_executor(
                None, self._restore_file_sync, str(self.current_backup), str(self.current_file)
            )
            
            if success:
                self.log('文件恢复成功！', 'success')
                self.update_status('文件恢复完成')
                ui.notify('文件恢复成功！', type='positive')
            else:
                self.log('文件恢复失败', 'error')
                self.update_status('文件恢复失败')
                ui.notify('文件恢复失败', type='negative')
                
        except Exception as ex:
            self.log(f'恢复过程中发生错误: {str(ex)}', 'error')
            self.update_status('恢复失败')
            ui.notify(f'恢复失败: {str(ex)}', type='negative')
    
    async def show_confirm_dialog(self) -> bool:
        """显示确认对话框"""
        result = {'confirmed': False}
        
        with ui.dialog() as dialog, ui.card():
            ui.label('确认恢复文件').classes('text-lg font-bold')
            ui.separator()
            
            with ui.column().classes('gap-2 mt-4'):
                ui.label('即将执行以下操作：')
                ui.label(f'• 源文件: {self.current_backup.name}').classes('text-sm')
                ui.label(f'• 目标文件: {self.current_file.name}').classes('text-sm')
                ui.label('• 目标文件将被覆盖').classes('text-sm text-red-500')
            
            with ui.row().classes('gap-2 mt-4'):
                ui.button(
                    '确认恢复', 
                    on_click=lambda: self.confirm_action(dialog, result, True)
                ).classes('bg-green-500')
                ui.button(
                    '取消', 
                    on_click=lambda: self.confirm_action(dialog, result, False)
                ).classes('bg-gray-500')
        
        dialog.open()
        
        # 等待用户选择
        while dialog.value is None:
            await asyncio.sleep(0.1)
        
        return result['confirmed']
    
    def confirm_action(self, dialog, result, confirmed):
        """确认操作"""
        result['confirmed'] = confirmed
        dialog.close()
    
    def clear_selection(self):
        """清除选择"""
        self.current_file = None
        self.current_backup = None
        
        # 清除显示
        self.file_info_card.clear()
        with self.file_info_card:
            ui.label('暂无文件选择').classes('text-gray-500')
        
        self.backup_info_card.clear()
        with self.backup_info_card:
            ui.label('暂无备份文件').classes('text-gray-500')
        self.update_status('等待文件选择...')
        if self.restore_button:
            self.restore_button.props('disabled=true')
            self.restore_button.update()
        
        self.log('已清除所有选择')
    def handle_dropped_file(self, file_path: str):
        """处理拖拽的文件"""
        try:
            if os.path.exists(file_path):
                # 异步调用文件处理
                asyncio.create_task(self.handle_file_selection(file_path))
            else:
                self.log(f'拖拽的文件不存在: {file_path}', 'error')
                ui.notify('拖拽的文件不存在', type='negative')
        except Exception as ex:
            self.log(f'处理拖拽文件失败: {str(ex)}', 'error')
            ui.notify(f'处理拖拽文件失败: {str(ex)}', type='negative')
    
    def handle_upload(self, event):
        """处理文件上传事件"""
        try:
            # 获取上传的文件
            if hasattr(event, 'content') and hasattr(event, 'name'):
                # 创建临时文件来模拟本地文件选择
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, event.name)
                
                # 保存上传的文件内容到临时文件
                with open(temp_file_path, 'wb') as f:
                    f.write(event.content)
                
                self.log(f'文件已上传: {event.name}')
                # 处理上传的文件
                asyncio.create_task(self.handle_file_selection(temp_file_path))
            else:
                ui.notify('文件上传格式不正确', type='negative')
        except Exception as ex:
            self.log(f'处理上传文件失败: {str(ex)}', 'error')
            ui.notify(f'处理上传失败: {str(ex)}', type='negative')


def main():
    """主函数"""
    # 创建应用实例
    app = BakRApp()
    
    # 运行应用
    ui.run(
        title='BakR - 智能备份文件恢复工具',
        port=8080,
        show=True,
        reload=False
    )


if __name__ == '__main__':
    main()
