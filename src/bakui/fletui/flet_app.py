"""
BakU Flet UI 应用
现代化的备份文件恢复工具图形界面
"""
import os
import sys
import threading
import time
import math
from pathlib import Path
from typing import List, Optional, Dict, Any

import flet as ft
from flet import (
    Page, AppBar, NavigationRail, NavigationRailDestination, Container, 
    Column, Row, Text, ElevatedButton, FilledButton, OutlinedButton,
    TextField, Dropdown, ProgressBar, ProgressRing, Divider,
    Card, ListTile, DataTable, DataColumn, DataRow, DataCell,
    Icon, IconButton, Tabs, Tab, ScrollMode, MainAxisAlignment,
    CrossAxisAlignment, Alignment, BorderRadius, Margin, Padding,
    Colors, Icons, FilePickerResultEvent, FilePicker, DragTarget,
    Draggable, SnackBar, AlertDialog, Banner,
    TextButton, Theme, ThemeMode
)

# 添加项目路径以导入核心模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from baku.core.multi_file_manager import MultiFileManager
from baku.core.file_queue import FileQueueItem, FileStatus, BackupInfo
from baku.core.backup_finder import BackupFinder
from baku.core.backup_restorer import BackupRestorer
from loguru import logger


class BakuFletApp:
    """BakU Flet 应用主类"""
    
    def __init__(self):
        self.file_manager = MultiFileManager()
        self.file_manager.set_progress_callback(self._on_progress_update)
        
        # UI 组件引用
        self.page: Optional[Page] = None
        self.file_picker: Optional[FilePicker] = None
        
        # 文件列表和状态显示
        self.file_list_column: Optional[Column] = None
        self.status_text: Optional[Text] = None
        self.progress_bar: Optional[ProgressBar] = None
        self.progress_text: Optional[Text] = None
        
        # 统计信息
        self.stats_row: Optional[Row] = None
        
        # 操作按钮
        self.scan_button: Optional[ElevatedButton] = None
        self.restore_button: Optional[ElevatedButton] = None
        self.clear_button: Optional[OutlinedButton] = None
        
        # 当前选中的文件
        self.selected_file_id: Optional[str] = None
        
        # 状态
        self.is_processing = False
    
    def build_app(self, page: Page):
        """构建应用界面"""
        self.page = page
        page.title = "BakU - 备份文件恢复工具"
        page.theme_mode = ThemeMode.LIGHT
        page.window_width = 1200
        page.window_height = 800
        page.window_min_width = 800
        page.window_min_height = 600
        
        # 创建文件选择器
        self.file_picker = FilePicker(on_result=self._on_file_picker_result)
        page.overlay.append(self.file_picker)
        
        # 构建主界面
        page.add(self._build_main_layout())
        
        # 初始化状态
        self._update_ui()
        page.update()
    
    def _build_main_layout(self) -> Container:
        """构建主布局"""
        return Container(
            content=Column([
                self._build_header(),
                Divider(height=1),
                self._build_body(),
                Divider(height=1),
                self._build_footer(),
            ], spacing=0),
            expand=True,
            padding=0,
        )
    
    def _build_header(self) -> Container:
        """构建顶部标题栏"""
        return Container(
            content=Row([
                Icon(Icons.BACKUP, size=32, color=Colors.BLUE_600),
                Text(
                    "BakU 备份恢复工具",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=Colors.BLUE_800
                ),
                Container(expand=True),  # 占位符
                Row([
                    OutlinedButton(
                        "添加文件",
                        icon=Icons.ADD_CIRCLE_OUTLINE,
                        on_click=self._on_add_file_click,
                    ),
                    ElevatedButton(
                        "扫描备份",
                        icon=Icons.SEARCH,
                        on_click=self._on_scan_click,
                        ref=ft.Ref[ElevatedButton]()
                    ),
                    FilledButton(
                        "恢复文件",
                        icon=Icons.RESTORE,
                        on_click=self._on_restore_click,
                        ref=ft.Ref[FilledButton]()
                    ),
                ], spacing=10),
            ], alignment=MainAxisAlignment.SPACE_BETWEEN),
            padding=Padding(20, 15, 20, 15),
            bgcolor=Colors.BLUE_50,
        )
    
    def _build_body(self) -> Container:
        """构建主体内容"""
        return Container(
            content=Row([
                # 左侧：文件拖拽区域和操作面板
                Container(
                    content=Column([
                        self._build_file_drop_area(),
                        Divider(height=1),
                        self._build_control_panel(),
                    ], spacing=10),
                    width=350,
                    padding=10,
                ),
                  # 中间：分隔线
                Container(
                    width=1,
                    bgcolor=Colors.GREY_300,
                ),
                
                # 右侧：文件列表和详情
                Container(
                    content=Column([
                        self._build_file_list_header(),
                        self._build_file_list(),
                        self._build_progress_section(),
                    ], spacing=10),
                    expand=True,
                    padding=10,
                ),
            ], spacing=0),
            expand=True,
        )
    
    def _build_file_drop_area(self) -> Container:
        """构建文件拖拽区域"""
        return Container(
            content=Column([
                Icon(Icons.CLOUD_UPLOAD, size=48, color=Colors.BLUE_400),                Text(
                    "拖拽文件到此处",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=Colors.BLUE_600
                ),
                Text(
                    "或点击下方按钮选择文件",
                    size=12,
                    color=Colors.GREY_600
                ),
                Container(height=10),
                OutlinedButton(
                    "浏览文件",
                    icon=Icons.FOLDER_OPEN,
                    on_click=lambda _: self.file_picker.pick_files(
                        allow_multiple=True,
                        dialog_title="选择要恢复的文件"
                    ),
                ),
            ], 
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=8
            ),
            height=180,
            border=ft.border.all(2, Colors.BLUE_200),
            border_radius=BorderRadius(8, 8, 8, 8),
            bgcolor=Colors.BLUE_50,
            alignment=ft.alignment.center,
            padding=20,
        )
    
    def _build_control_panel(self) -> Column:
        """构建控制面板"""
        self.scan_button = ElevatedButton(
            "扫描所有备份",
            icon=Icons.SEARCH,
            on_click=self._on_batch_scan_click,
            width=200,
        )
        
        self.restore_button = FilledButton(
            "批量恢复",
            icon=Icons.RESTORE,
            on_click=self._on_batch_restore_click,
            width=200,
        )
        
        self.clear_button = OutlinedButton(
            "清空列表",
            icon=Icons.CLEAR_ALL,
            on_click=self._on_clear_click,
            width=200,
        )
        
        return Column([
            Text("操作", size=16, weight=ft.FontWeight.BOLD),
            self.scan_button,
            self.restore_button,
            self.clear_button,
            Divider(height=1),
            self._build_stats_section(),
        ], spacing=10)
    
    def _build_stats_section(self) -> Column:
        """构建统计信息区域"""
        self.stats_row = Column([
            Text("文件统计", size=16, weight=ft.FontWeight.BOLD),
            Row([
                Text("总数: "),
                Text("0", weight=ft.FontWeight.BOLD, color=Colors.BLUE_600),
            ]),
            Row([
                Text("已扫描: "),
                Text("0", weight=ft.FontWeight.BOLD, color=Colors.GREEN_600),
            ]),
            Row([
                Text("可恢复: "),
                Text("0", weight=ft.FontWeight.BOLD, color=Colors.ORANGE_600),
            ]),
            Row([
                Text("已完成: "),
                Text("0", weight=ft.FontWeight.BOLD, color=Colors.GREEN_800),
            ]),
        ], spacing=5)
        
        return self.stats_row
    
    def _build_file_list_header(self) -> Row:
        """构建文件列表标题"""
        return Row([
            Text(
                "文件列表", 
                size=18, 
                weight=ft.FontWeight.BOLD
            ),
            Container(expand=True),
            Text(
                "双击文件查看备份详情",
                size=12,
                color=Colors.GREY_600
            ),
        ])
    
    def _build_file_list(self) -> Container:
        """构建文件列表"""
        self.file_list_column = Column(
            spacing=5,
            scroll=ScrollMode.AUTO,
        )
        return Container(
            content=self.file_list_column,
            expand=True,
            border=ft.border.all(1, Colors.GREY_300),
            border_radius=BorderRadius(8, 8, 8, 8),
            padding=10,
        )
    
    def _build_progress_section(self) -> Column:
        """构建进度显示区域"""
        self.progress_bar = ProgressBar(
            width=400,
            visible=False,
            color=Colors.BLUE_600,
            bgcolor=Colors.BLUE_100,
        )
        
        self.progress_text = Text(
            "",
            size=12,
            color=Colors.GREY_700,
            visible=False,
        )
        self.status_text = Text(
            "就绪",
            size=14,
            color=Colors.GREEN_600,
            weight=ft.FontWeight.W_500,
        )
        
        return Column([
            Row([
                Icon(Icons.INFO_OUTLINE, size=16),
                self.status_text,
            ], spacing=5),
            self.progress_bar,
            self.progress_text,
        ], spacing=5)
    
    def _build_footer(self) -> Container:
        """构建底部状态栏"""
        return Container(
            content=Row([
                Text(
                    "BakU v2.0 - 智能备份文件恢复工具",
                    size=12,
                    color=Colors.GREY_600
                ),
                Container(expand=True),
                Text(
                    "Powered by Flet",
                    size=12,
                    color=Colors.GREY_500
                ),            ]),
            padding=Padding(20, 10, 20, 10),
            bgcolor=Colors.GREY_100,
        )
    
    def _create_file_item_card(self, item: FileQueueItem) -> Card:
        """创建文件项卡片"""
        # 状态图标和颜色
        status_config = {
            FileStatus.PENDING: (Icons.SCHEDULE, Colors.ORANGE_600, "等待处理"),
            FileStatus.PROCESSING: (Icons.REFRESH, Colors.BLUE_600, "处理中"),
            FileStatus.COMPLETED: (Icons.CHECK_CIRCLE, Colors.GREEN_600, "已完成"),
            FileStatus.ERROR: (Icons.ERROR, Colors.RED_600, "错误"),
            FileStatus.CANCELLED: (Icons.CANCEL, Colors.GREY_600, "已取消"),
        }
        
        icon_name, color, status_text = status_config.get(
            item.status, 
            (Icons.HELP, Colors.GREY_600, "未知")
        )
        
        # 文件大小格式化
        size_str = self._format_file_size(item.size)
        
        # 备份信息
        backup_count = len(item.backup_files)
        backup_text = f"{backup_count} 个备份" if backup_count > 0 else "无备份"
        
        return Card(
            content=Container(
                content=Column([
                    Row([
                        Icon(icon_name, color=color, size=20),
                        Container(
                            content=Column([                                Text(
                                    item.name,
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                Text(
                                    f"{size_str} • {backup_text}",
                                    size=12,
                                    color=Colors.GREY_600,
                                ),
                            ], spacing=2),
                            expand=True,
                        ),
                        Container(
                            content=Column([                                Text(
                                    status_text,
                                    size=12,
                                    color=color,
                                    weight=ft.FontWeight.W_500,
                                ),
                                Text(
                                    item.message or "",
                                    size=10,
                                    color=Colors.GREY_500,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ) if item.message else Container(),
                            ], spacing=2, horizontal_alignment=CrossAxisAlignment.END),
                            width=120,
                        ),
                    ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                    
                    # 如果有备份文件，显示操作按钮
                    Row([
                        Container(expand=True),
                        *self._build_item_action_buttons(item),
                    ]) if backup_count > 0 else Container(),
                ], spacing=8),
                padding=Padding(15, 12, 15, 12),
            ),
            margin=Margin(0, 2, 0, 2),
            elevation=1,
        )
    
    def _build_item_action_buttons(self, item: FileQueueItem) -> List[ft.Control]:
        """构建文件项操作按钮"""
        buttons = []
        
        # 查看详情按钮
        buttons.append(
            TextButton(
                "详情",
                icon=Icons.INFO_OUTLINE,
                on_click=lambda e, item_id=item.id: self._show_file_details(item_id),
            )
        )
        
        # 如果有备份且未恢复，显示恢复按钮
        if item.backup_files and item.status != FileStatus.COMPLETED:
            buttons.append(
                ElevatedButton(
                    "恢复",
                    icon=Icons.RESTORE,
                    height=32,
                    on_click=lambda e, item_id=item.id: self._restore_single_file(item_id),
                )
            )
        
        return buttons
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        import math
        
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    # 事件处理方法
    def _on_file_picker_result(self, e: FilePickerResultEvent):
        """处理文件选择结果"""
        if e.files:
            for file in e.files:
                self._add_file_to_queue(file.path, file.name, file.size)
            self._update_ui()
            self.page.update()
    
    def _on_add_file_click(self, e):
        """添加文件按钮点击"""
        self.file_picker.pick_files(
            allow_multiple=True,
            dialog_title="选择要恢复的文件"
        )
    
    def _on_scan_click(self, e):
        """扫描按钮点击"""
        self._start_batch_scan()
    
    def _on_restore_click(self, e):
        """恢复按钮点击"""
        self._start_batch_restore()
    
    def _on_batch_scan_click(self, e):
        """批量扫描按钮点击"""
        self._start_batch_scan()
    
    def _on_batch_restore_click(self, e):
        """批量恢复按钮点击"""
        self._start_batch_restore()
    
    def _on_clear_click(self, e):
        """清空按钮点击"""
        self._show_confirm_dialog(
            "确认清空",
            "确定要清空所有文件吗？此操作不可撤销。",
            self._clear_all_files
        )
    
    def _add_file_to_queue(self, file_path: str, file_name: str, file_size: int):
        """添加文件到队列"""
        try:
            item_id = self.file_manager.add_file_from_info(
                name=file_name,
                size=file_size,
                file_path=file_path,
            )
            
            if item_id:
                self._show_snack_bar(f"已添加文件: {file_name}", Colors.GREEN_600)
                logger.info(f"文件已添加到队列: {file_name}")
            else:
                self._show_snack_bar(f"文件已存在: {file_name}", Colors.ORANGE_600)
                
        except Exception as ex:
            self._show_snack_bar(f"添加文件失败: {str(ex)}", Colors.RED_600)
            logger.error(f"添加文件失败: {ex}")
    
    def _start_batch_scan(self):
        """开始批量扫描"""
        if self.is_processing:
            self._show_snack_bar("正在处理中，请稍候", Colors.ORANGE_600)
            return
        
        pending_files = [
            item for item in self.file_manager.get_all_items()
            if item.status == FileStatus.PENDING and item.path
        ]
        
        if not pending_files:
            self._show_snack_bar("没有待扫描的文件", Colors.ORANGE_600)
            return
        
        def scan_thread():
            try:
                self.is_processing = True
                self._update_processing_state(True, "正在扫描备份文件...")
                
                success = self.file_manager.batch_scan_backups()
                
                if success:
                    self._show_snack_bar("扫描完成", Colors.GREEN_600)
                else:
                    self._show_snack_bar("扫描失败", Colors.RED_600)
                    
            except Exception as ex:
                self._show_snack_bar(f"扫描出错: {str(ex)}", Colors.RED_600)
                logger.error(f"批量扫描出错: {ex}")
            finally:
                self.is_processing = False
                self._update_processing_state(False)
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def _start_batch_restore(self):
        """开始批量恢复"""
        if self.is_processing:
            self._show_snack_bar("正在处理中，请稍候", Colors.ORANGE_600)
            return
        
        restorable_items = self.file_manager.file_queue.get_restorable_items()
        
        if not restorable_items:
            self._show_snack_bar("没有可恢复的文件", Colors.ORANGE_600)
            return
        
        def confirm_restore():
            def restore_thread():
                try:
                    self.is_processing = True
                    self._update_processing_state(True, "正在恢复文件...")
                    
                    success = self.file_manager.batch_restore_files()
                    
                    if success:
                        self._show_snack_bar("恢复完成", Colors.GREEN_600)
                    else:
                        self._show_snack_bar("恢复失败", Colors.RED_600)
                        
                except Exception as ex:
                    self._show_snack_bar(f"恢复出错: {str(ex)}", Colors.RED_600)
                    logger.error(f"批量恢复出错: {ex}")
                finally:
                    self.is_processing = False
                    self._update_processing_state(False)
            
            threading.Thread(target=restore_thread, daemon=True).start()
        
        self._show_confirm_dialog(
            "确认恢复",
            f"确定要恢复 {len(restorable_items)} 个文件吗？\n原文件将备份为 .new 扩展名。",
            confirm_restore
        )
    
    def _restore_single_file(self, item_id: str):
        """恢复单个文件"""
        if self.is_processing:
            self._show_snack_bar("正在处理中，请稍候", Colors.ORANGE_600)
            return
        
        item = self.file_manager.file_queue.get_item(item_id)
        if not item or not item.backup_files:
            self._show_snack_bar("文件不存在或无备份", Colors.RED_600)
            return
        
        def confirm_restore():
            def restore_thread():
                try:
                    self.is_processing = True
                    self._update_processing_state(True, f"正在恢复 {item.name}...")
                    
                    success = self.file_manager.restore_file(item_id)
                    
                    if success:
                        self._show_snack_bar(f"{item.name} 恢复成功", Colors.GREEN_600)
                    else:
                        self._show_snack_bar(f"{item.name} 恢复失败", Colors.RED_600)
                        
                except Exception as ex:
                    self._show_snack_bar(f"恢复出错: {str(ex)}", Colors.RED_600)
                    logger.error(f"单文件恢复出错: {ex}")
                finally:
                    self.is_processing = False
                    self._update_processing_state(False)
            
            threading.Thread(target=restore_thread, daemon=True).start()
        
        self._show_confirm_dialog(
            "确认恢复",
            f"确定要恢复 {item.name} 吗？\n原文件将备份为 .new 扩展名。",
            confirm_restore        )
    
    def _clear_all_files(self):
        """清空所有文件"""
        self.file_manager.clear_queue()
        self._update_ui()
        self._show_snack_bar("文件列表已清空", Colors.GREEN_600)
    
    def _show_file_details(self, item_id: str):
        """显示文件详情对话框"""
        item = self.file_manager.file_queue.get_item(item_id)
        if not item:
            return
        
        # 构建备份文件列表
        backup_list = []
        for backup in item.backup_files:
            backup_list.append(
                ListTile(
                    leading=Icon(Icons.BACKUP, color=Colors.BLUE_600),
                    title=Text(backup.name),                subtitle=Text(f"大小: {backup.size_str} | 修改时间: {backup.modified.strftime('%Y-%m-%d %H:%M:%S')}"),
                )
            )
        
        content = Column([
            Text(f"文件: {item.name}", size=18, weight=ft.FontWeight.BOLD),
            Text(f"路径: {item.path}"),
            Text(f"大小: {self._format_file_size(item.size)}"),
            Text(f"状态: {item.status.value}"),
            Text(f"消息: {item.message or '无'}"),
            Divider(),
            Text("备份文件:", size=16, weight=ft.FontWeight.BOLD),
        ] + (backup_list if backup_list else [Text("暂无备份文件", color=Colors.GREY_600)]), scroll=ScrollMode.AUTO)
        
        dialog = AlertDialog(
            title=Text("文件详情"),
            content=Container(content=content, height=400, width=500),
            actions=[
                TextButton("关闭", on_click=lambda e: self._close_dialog()),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_confirm_dialog(self, title: str, content: str, on_confirm):
        """显示确认对话框"""
        def handle_confirm(e):
            self._close_dialog()
            on_confirm()
        
        def handle_cancel(e):
            self._close_dialog()
        
        dialog = AlertDialog(
            title=Text(title),
            content=Text(content),
            actions=[
                TextButton("取消", on_click=handle_cancel),
                ElevatedButton("确认", on_click=handle_confirm),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _close_dialog(self):
        """关闭对话框"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def _show_snack_bar(self, message: str, color=Colors.BLUE_600):
        """显示消息条"""
        snack_bar = SnackBar(
            content=Text(message, color=Colors.WHITE),
            bgcolor=color,
            duration=3000,
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()
    
    def _update_processing_state(self, is_processing: bool, message: str = ""):
        """更新处理状态"""
        if self.progress_bar:
            self.progress_bar.visible = is_processing
        
        if self.progress_text:
            self.progress_text.value = message
            self.progress_text.visible = is_processing and bool(message)
        
        if self.status_text:
            if is_processing:
                self.status_text.value = "处理中..."
                self.status_text.color = Colors.BLUE_600
            else:
                self.status_text.value = "就绪"
                self.status_text.color = Colors.GREEN_600
        
        # 更新按钮状态
        if self.scan_button:
            self.scan_button.disabled = is_processing
        if self.restore_button:
            self.restore_button.disabled = is_processing
        
        self.page.update()
    
    def _on_progress_update(self, progress: float, message: str):
        """进度更新回调"""
        if self.progress_bar:
            self.progress_bar.value = progress
        
        if self.progress_text:
            self.progress_text.value = message
        
        # 在主线程中更新UI
        try:
            self.page.update()
        except:
            pass  # 忽略更新错误
        
        # 如果完成，更新文件列表
        if progress >= 1.0:
            time.sleep(0.1)  # 短暂延迟
            self._update_ui()
    
    def _update_ui(self):
        """更新UI显示"""
        # 更新文件列表
        if self.file_list_column:
            self.file_list_column.controls.clear()
            
            items = self.file_manager.get_all_items()
            if items:
                for item in items:
                    self.file_list_column.controls.append(
                        self._create_file_item_card(item)
                    )
            else:
                self.file_list_column.controls.append(
                    Container(
                        content=Column([
                            Icon(Icons.INBOX, size=48, color=Colors.GREY_400),
                            Text(
                                "暂无文件",
                                size=16,
                                color=Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            Text(
                                "拖拽文件到左侧区域或点击添加按钮",
                                size=12,
                                color=Colors.GREY_500,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ], 
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        spacing=10),
                        alignment=ft.alignment.center,
                        height=200,
                    )
                )
        
        # 更新统计信息
        if self.stats_row:
            stats = self.file_manager.get_queue_summary()
            stats_data = stats['stats']
            
            # 更新统计数字
            stats_controls = self.stats_row.controls[1:]  # 跳过标题
            if len(stats_controls) >= 4:
                stats_controls[0].controls[1].value = str(stats_data['total'])
                stats_controls[1].controls[1].value = str(stats_data['completed'])
                stats_controls[2].controls[1].value = str(stats['restorable_items'])
                stats_controls[3].controls[1].value = str(stats_data['completed'])
        
        try:
            self.page.update()
        except:
            pass  # 忽略更新错误


def main():
    """主函数"""
    app = BakuFletApp()
    ft.app(target=app.build_app, view=ft.WEB_BROWSER)


if __name__ == "__main__":
    main()
