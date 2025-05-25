"""
多文件管理核心功能
CLI和Web界面共用的多文件处理逻辑
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import threading
import time
from .file_queue import FileQueue, FileQueueItem, FileStatus, BackupInfo
from .backup_finder import BackupFinder
from .backup_restorer import BackupRestorer
from loguru import logger


class MultiFileManager:
    """多文件管理核心类"""
    
    def __init__(self, backup_finder: Optional[BackupFinder] = None, 
                 backup_restorer: Optional[BackupRestorer] = None):
        self.backup_finder = backup_finder or BackupFinder()
        self.backup_restorer = backup_restorer or BackupRestorer()
        self.file_queue = FileQueue()
        self.queue = self.file_queue  # 别名，为了兼容性
        self._is_processing = False
        self._cancel_requested = False
        self._progress_callback: Optional[Callable[[float, str], None]] = None
        
    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """设置进度回调函数"""
        self._progress_callback = callback
    
    def _report_progress(self, progress: float, message: str):
        """报告进度"""
        if self._progress_callback:
            self._progress_callback(progress, message)
    
    def add_file_from_info(self, name: str, size: int, file_path: Optional[str] = None,
                          last_modified: Optional[int] = None) -> str:
        """从文件信息添加文件到队列"""
        # 生成唯一ID
        timestamp = last_modified or int(datetime.now().timestamp() * 1000)
        item_id = f"{name}_{size}_{timestamp}"
        
        # 创建队列项
        queue_item = FileQueueItem(
            id=item_id,
            name=name,
            path=Path(file_path) if file_path else None,
            size=size,
            status=FileStatus.PENDING,
            message="等待处理" if file_path else "等待提供完整文件路径"
        )
        
        if self.file_queue.add_item(queue_item):
            return item_id
        else:
            # 如果添加失败（可能是重复），返回现有项的ID
            existing_item = self.file_queue.get_item(item_id)
            return existing_item.id if existing_item else ""
    
    def add_files_from_drop_data(self, dropped_files: List[Dict[str, Any]]) -> List[str]:
        """从拖拽数据批量添加文件"""
        added_ids = []
        
        for file_data in dropped_files:
            item_id = self.add_file_from_info(
                name=file_data['name'],
                size=file_data['size'],
                last_modified=file_data.get('lastModified')
            )
            if item_id:
                added_ids.append(item_id)
        
        return added_ids
    
    def set_file_path(self, item_id: str, file_path: str) -> bool:
        """为文件项设置完整路径"""
        item = self.file_queue.get_item(item_id)
        if not item:
            return False
        
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return False
        
        # 验证文件名和大小是否匹配
        if path.name != item.name:
            return False
        
        try:
            actual_size = path.stat().st_size
            if actual_size != item.size:
                return False
        except OSError:
            return False
        
        item.path = path
        item.update_status(FileStatus.PENDING, "路径已设置，等待扫描")
        return True
    
    def remove_file(self, item_id: str) -> bool:
        """从队列中移除文件"""
        return self.file_queue.remove_item(item_id)
    
    def clear_queue(self):
        """清空文件队列"""
        self.file_queue.clear()
    
    def scan_file_backups(self, item_id: str) -> bool:
        """扫描指定文件的备份"""
        item = self.file_queue.get_item(item_id)
        if not item or not item.path:
            return False
        try:
            item.update_status(FileStatus.PROCESSING, "正在扫描备份文件...")
            self._report_progress(0.0, f"扫描 {item.name} 的备份文件...")
            
            # 使用备份查找器 - backup_finder返回Path对象或None
            backup_path = self.backup_finder.find_nearest_backup(item.path)
            
            if backup_path and backup_path.exists():
                stat = backup_path.stat()
                backup_info = BackupInfo(
                    path=backup_path,
                    name=backup_path.name,
                    size=stat.st_size,
                    size_str=self._format_file_size(stat.st_size),
                    modified=datetime.fromtimestamp(stat.st_mtime),
                    similarity=1.0,  # 默认相似度
                    file_type=backup_path.suffix
                )
                
                item.add_backup(backup_info)
                item.update_status(FileStatus.COMPLETED, f"找到备份文件")
                self._report_progress(1.0, f"{item.name} 扫描完成")
                return True
            else:
                item.update_status(FileStatus.ERROR, "未找到备份文件")
            
            self._report_progress(1.0, f"{item.name} 扫描完成（无备份）")
            return False
            
        except Exception as ex:
            item.update_status(FileStatus.ERROR, f"扫描失败: {str(ex)}")
            self._report_progress(1.0, f"{item.name} 扫描失败")
            return False
    
    def batch_scan_backups(self) -> bool:
        """批量扫描所有文件的备份"""
        if self._is_processing:
            return False
        # 获取所有需要扫描的文件（有路径且状态为PENDING）
        pending_files = [
            item for item in self.file_queue.items
            if item.status == FileStatus.PENDING and item.path
        ]
        if not pending_files:
            return False
        self._is_processing = True
        self._cancel_requested = False
        try:
            total_files = len(pending_files)
            self._report_progress(0.0, f"开始批量扫描 {total_files} 个文件...")
            for i, item in enumerate(pending_files):
                if self._cancel_requested:
                    break
                # 扫描单个文件
                self.scan_file_backups(item.id)
                # 更新总体进度
                progress = (i + 1) / total_files
                self._report_progress(progress, f"已扫描 {i + 1}/{total_files} 个文件")
                # 短暂暂停
                time.sleep(0.1)
            # 自动为有备份但未设置selected_backup的文件设置第一个备份
            for item in self.file_queue.items:
                if item.backup_files and not item.selected_backup:
                    item.set_selected_backup(item.backup_files[0].path)
            self._is_processing = False
            if self._cancel_requested:
                self._report_progress(1.0, "批量扫描已取消")
            else:
                self._report_progress(1.0, f"批量扫描完成，共处理 {total_files} 个文件")
            return not self._cancel_requested
        except Exception as ex:
            self._is_processing = False
            self._report_progress(1.0, f"批量扫描失败: {str(ex)}")
            return False
    
    def restore_file(self, item_id: str, backup_path: Optional[Path] = None) -> bool:
        """恢复指定文件"""
        item = self.file_queue.get_item(item_id)
        if not item or not item.path:
            logger.error(f"[restore_file] 未找到文件项或路径: item_id={item_id}")
            return False
        # 如果没有指定备份路径，使用已选择的备份
        if backup_path is None:
            backup_path = item.selected_backup
        if not backup_path or not backup_path.exists():
            logger.error(f"[restore_file] 没有可用的备份文件: item_id={item_id}, backup_path={backup_path}")
            item.update_status(FileStatus.ERROR, "没有可用的备份文件")
            return False
        try:
            item.update_status(FileStatus.PROCESSING, "正在恢复文件...")
            self._report_progress(0.0, f"恢复 {item.name}...")
            logger.info(f"[restore_file] 开始恢复: {item.name}, 源: {item.path}, 备份: {backup_path}")
            result = self.backup_restorer.restore_backup(item.path, backup_path)
            if result.get('success'):
                item.update_status(FileStatus.COMPLETED, "文件恢复成功")
                self._report_progress(1.0, f"{item.name} 恢复成功")
                logger.success(f"[restore_file] 恢复成功: {item.name}")
                return True
            else:
                error_msg = result.get('message', '未知错误')
                item.update_status(FileStatus.ERROR, f"恢复失败: {error_msg}")
                self._report_progress(1.0, f"{item.name} 恢复失败")
                logger.error(f"[restore_file] 恢复失败: {item.name}, 错误: {error_msg}")
                return False
        except Exception as ex:
            item.update_status(FileStatus.ERROR, f"恢复过程中发生错误: {str(ex)}")
            self._report_progress(1.0, f"{item.name} 恢复出错")
            logger.exception(f"[restore_file] 恢复出错: {item.name}, 错误: {ex}")
            return False
    
    def set_selected_backup(self, item_id: str, backup_path: Path) -> bool:
        """为文件项设置选中的备份"""
        item = self.file_queue.get_item(item_id)
        if not item:
            return False
        
        # 验证备份路径是否在备份列表中
        backup_paths = [backup.path for backup in item.backup_files]
        if backup_path not in backup_paths:
            return False
        
        item.set_selected_backup(backup_path)
        return True
    
    def batch_restore_files(self, item_ids: Optional[List[str]] = None) -> bool:
        """批量恢复文件"""
        if self._is_processing:
            logger.warning("[batch_restore_files] 已有批处理在进行中，操作被拒绝")
            return False
        # 如果没有指定文件ID，则恢复所有可恢复的文件
        if item_ids is None:
            restorable_items = self.file_queue.get_restorable_items()
        else:
            restorable_items = [
                self.file_queue.get_item(item_id) 
                for item_id in item_ids
                if self.file_queue.get_item(item_id) and 
                   self.file_queue.get_item(item_id).selected_backup
            ]
            restorable_items = [item for item in restorable_items if item]
        if not restorable_items:
            logger.warning("[batch_restore_files] 没有可恢复的文件")
            return False
        self._is_processing = True
        self._cancel_requested = False
        try:
            total_files = len(restorable_items)
            success_count = 0
            self._report_progress(0.0, f"开始批量恢复 {total_files} 个文件...")
            logger.info(f"[batch_restore_files] 批量恢复开始，共 {total_files} 个文件")
            for i, item in enumerate(restorable_items):
                if self._cancel_requested:
                    logger.warning(f"[batch_restore_files] 批量恢复被取消，已处理 {i} 个文件")
                    break
                # 恢复单个文件
                if self.restore_file(item.id):
                    success_count += 1
                # 更新总体进度
                progress = (i + 1) / total_files
                self._report_progress(progress, f"已处理 {i + 1}/{total_files} 个文件")
                time.sleep(0.1)
            self._is_processing = False
            if self._cancel_requested:
                self._report_progress(1.0, f"批量恢复已取消，已成功恢复 {success_count} 个文件")
                logger.warning(f"[batch_restore_files] 批量恢复已取消，成功恢复 {success_count} 个文件")
            else:
                self._report_progress(1.0, f"批量恢复完成，成功恢复 {success_count}/{total_files} 个文件")
                logger.success(f"[batch_restore_files] 批量恢复完成，成功恢复 {success_count}/{total_files} 个文件")
            return not self._cancel_requested
        except Exception as ex:
            self._is_processing = False
            self._report_progress(1.0, f"批量恢复失败: {str(ex)}")
            logger.exception(f"[batch_restore_files] 批量恢复失败: {ex}")
            return False
    
    def cancel_batch_operation(self):
        """取消批处理操作"""
        self._cancel_requested = True
    
    def is_processing(self) -> bool:
        """检查是否正在处理"""
        return self._is_processing
    
    def get_queue_summary(self) -> Dict[str, Any]:
        """获取队列摘要信息"""
        stats = self.file_queue.get_stats()
        return {
            'total_files': stats['total'],
            'total_size': self.file_queue.get_total_size(),
            'stats': stats,
            'is_processing': self._is_processing,
            'items_with_backups': len(self.file_queue.get_items_with_backups()),
            'restorable_items': len(self.file_queue.get_restorable_items())
        }
    
    def get_all_items(self) -> List[FileQueueItem]:
        """获取所有队列项"""
        return self.file_queue.items.copy()
    
    def get_items_by_status(self, status: FileStatus) -> List[FileQueueItem]:
        """按状态获取文件项"""
        return self.file_queue.get_items_by_status(status)
    
    def save_queue(self, file_path: Path) -> bool:
        """保存队列到文件"""
        return self.file_queue.save_to_file(file_path)
    
    def load_queue(self, file_path: Path) -> bool:
        """从文件加载队列"""
        return self.file_queue.load_from_file(file_path)
    
    def export_status_report(self) -> str:
        """导出状态报告"""
        return self.file_queue.export_status_report()
    
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
