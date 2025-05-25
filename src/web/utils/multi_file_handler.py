"""
Streamlit专用多文件处理包装器
基于core.multi_file_manager的Streamlit界面适配
"""
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import time

# 添加core模块路径
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from core.multi_file_manager import MultiFileManager
from core.file_queue import FileStatus, FileQueueItem, BackupInfo
from core.backup_finder import BackupFinder
from core.backup_restorer import BackupRestorer


class StreamlitMultiFileHandler:
    """多文件处理器"""
    
    def __init__(self, backup_finder, backup_restorer):
        self.backup_finder = backup_finder
        self.backup_restorer = backup_restorer
        self.init_session_state()
    
    def init_session_state(self):
        """初始化session状态"""
        if 'file_queue' not in st.session_state:
            st.session_state.file_queue = []
        if 'batch_processing' not in st.session_state:
            st.session_state.batch_processing = False
        if 'batch_progress' not in st.session_state:
            st.session_state.batch_progress = 0.0
        if 'batch_stats' not in st.session_state:
            st.session_state.batch_stats = {
                'total': 0,
                'pending': 0,
                'processing': 0,
                'completed': 0,
                'error': 0
            }
    
    def add_files_from_drop(self, dropped_files: List[Dict[str, Any]]):
        """从拖拽数据添加文件到队列"""
        for file_data in dropped_files:
            # 检查是否已存在
            existing = any(
                item.name == file_data['name'] and item.size == file_data['size']
                for item in st.session_state.file_queue
            )
            
            if not existing:
                queue_item = FileQueueItem(
                    id=f"{file_data['name']}_{file_data['size']}_{file_data['lastModified']}",
                    name=file_data['name'],
                    path=None,  # 需要用户提供完整路径
                    size=file_data['size'],
                    status=FileStatus.PENDING,
                    message="等待提供完整文件路径"
                )
                st.session_state.file_queue.append(queue_item)
        
        self.update_batch_stats()
    
    def add_file_path(self, file_id: str, file_path: str) -> bool:
        """为文件项设置完整路径"""
        path = Path(file_path)
        if not path.exists():
            return False
        
        for item in st.session_state.file_queue:
            if item.id == file_id:
                item.path = path
                item.message = "路径已设置，等待扫描"
                return True
        return False
    
    def remove_file(self, file_id: str):
        """从队列中移除文件"""
        st.session_state.file_queue = [
            item for item in st.session_state.file_queue
            if item.id != file_id
        ]
        self.update_batch_stats()
    
    def clear_queue(self):
        """清空文件队列"""
        st.session_state.file_queue = []
        self.update_batch_stats()
    
    def update_batch_stats(self):
        """更新批处理统计"""
        stats = {
            'total': len(st.session_state.file_queue),
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'error': 0
        }
        
        for item in st.session_state.file_queue:
            if item.status == FileStatus.PENDING:
                stats['pending'] += 1
            elif item.status == FileStatus.PROCESSING:
                stats['processing'] += 1
            elif item.status == FileStatus.COMPLETED:
                stats['completed'] += 1
            elif item.status == FileStatus.ERROR:
                stats['error'] += 1
        
        st.session_state.batch_stats = stats
    
    def scan_file_backups(self, file_id: str) -> bool:
        """扫描指定文件的备份"""
        for item in st.session_state.file_queue:
            if item.id == file_id and item.path:
                try:
                    item.status = FileStatus.PROCESSING
                    item.message = "正在扫描备份文件..."
                    self.update_batch_stats()
                    
                    # 使用备份查找器
                    result = self.backup_finder.find_nearest_backup(str(item.path))
                    
                    if result and result.get('success') and result.get('backup_path'):
                        backup_path = Path(result['backup_path'])
                        if backup_path.exists():
                            stat = backup_path.stat()
                            item.backup_files = [{
                                'path': backup_path,
                                'name': backup_path.name,
                                'size': stat.st_size,
                                'size_str': self.format_file_size(stat.st_size),
                                'modified': datetime.fromtimestamp(stat.st_mtime),
                                'similarity': result.get('similarity', 1.0),
                                'type': backup_path.suffix
                            }]
                            item.status = FileStatus.COMPLETED
                            item.message = f"找到 {len(item.backup_files)} 个备份文件"
                        else:
                            item.status = FileStatus.ERROR
                            item.message = "备份文件不存在"
                    else:
                        item.status = FileStatus.ERROR
                        item.message = "未找到备份文件"
                    
                    self.update_batch_stats()
                    return True
                    
                except Exception as ex:
                    item.status = FileStatus.ERROR
                    item.message = f"扫描失败: {str(ex)}"
                    self.update_batch_stats()
                    return False
        return False
    
    def batch_scan_backups(self) -> bool:
        """批量扫描所有文件的备份"""
        if st.session_state.batch_processing:
            return False
        
        st.session_state.batch_processing = True
        st.session_state.batch_progress = 0.0
        
        try:
            # 获取所有有路径且状态为PENDING的文件
            pending_files = [
                item for item in st.session_state.file_queue
                if item.status == FileStatus.PENDING and item.path
            ]
            
            if not pending_files:
                st.session_state.batch_processing = False
                return False
            
            total_files = len(pending_files)
            
            for i, item in enumerate(pending_files):
                if not st.session_state.batch_processing:  # 检查是否被取消
                    break
                
                self.scan_file_backups(item.id)
                
                # 更新进度
                progress = (i + 1) / total_files
                st.session_state.batch_progress = progress
                
                # 短暂暂停以显示进度
                time.sleep(0.1)
            
            st.session_state.batch_processing = False
            st.session_state.batch_progress = 1.0
            return True
            
        except Exception as ex:
            st.session_state.batch_processing = False
            st.error(f"批量扫描失败: {str(ex)}")
            return False
    
    def restore_file(self, file_id: str, backup_path: Path) -> bool:
        """恢复指定文件"""
        for item in st.session_state.file_queue:
            if item.id == file_id and item.path:
                try:
                    item.status = FileStatus.PROCESSING
                    item.message = "正在恢复文件..."
                    self.update_batch_stats()
                    
                    result = self.backup_restorer.restore_backup(item.path, backup_path)
                    
                    if result.get('success'):
                        item.status = FileStatus.COMPLETED
                        item.message = "文件恢复成功"
                        self.update_batch_stats()
                        return True
                    else:
                        error_msg = result.get('message', '未知错误')
                        item.status = FileStatus.ERROR
                        item.message = f"恢复失败: {error_msg}"
                        self.update_batch_stats()
                        return False
                        
                except Exception as ex:
                    item.status = FileStatus.ERROR
                    item.message = f"恢复过程中发生错误: {str(ex)}"
                    self.update_batch_stats()
                    return False
        return False
    
    def batch_restore_files(self) -> bool:
        """批量恢复文件"""
        if st.session_state.batch_processing:
            return False
        
        st.session_state.batch_processing = True
        st.session_state.batch_progress = 0.0
        
        try:
            # 获取所有有备份文件且已选择备份的文件
            restorable_files = [
                item for item in st.session_state.file_queue
                if item.backup_files and item.selected_backup and item.status == FileStatus.COMPLETED
            ]
            
            if not restorable_files:
                st.session_state.batch_processing = False
                return False
            
            total_files = len(restorable_files)
            
            for i, item in enumerate(restorable_files):
                if not st.session_state.batch_processing:  # 检查是否被取消
                    break
                
                self.restore_file(item.id, item.selected_backup)
                
                # 更新进度
                progress = (i + 1) / total_files
                st.session_state.batch_progress = progress
                
                # 短暂暂停以显示进度
                time.sleep(0.1)
            
            st.session_state.batch_processing = False
            st.session_state.batch_progress = 1.0
            return True
            
        except Exception as ex:
            st.session_state.batch_processing = False
            st.error(f"批量恢复失败: {str(ex)}")
            return False
    
    def cancel_batch_operation(self):
        """取消批处理操作"""
        st.session_state.batch_processing = False
    
    def get_queue_summary(self) -> Dict[str, Any]:
        """获取队列摘要信息"""
        return {
            'total_files': len(st.session_state.file_queue),
            'total_size': sum(item.size for item in st.session_state.file_queue),
            'stats': st.session_state.batch_stats,
            'is_processing': st.session_state.batch_processing,
            'progress': st.session_state.batch_progress
        }
    
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
    
    def export_queue_status(self) -> str:
        """导出队列状态为文本"""
        lines = ["BakR 文件队列状态报告", "=" * 30, ""]
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"总文件数: {len(st.session_state.file_queue)}")
        lines.append("")
        
        for item in st.session_state.file_queue:
            lines.append(f"文件: {item.name}")
            lines.append(f"  状态: {item.status.value}")
            lines.append(f"  路径: {item.path or '未设置'}")
            lines.append(f"  大小: {self.format_file_size(item.size)}")
            lines.append(f"  消息: {item.message}")
            if item.backup_files:
                lines.append(f"  备份文件数: {len(item.backup_files)}")
            lines.append("")
        
        return "\n".join(lines)
