"""
文件队列核心数据结构
CLI和Web界面共用的文件队列管理
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
from loguru import logger


class FileStatus(Enum):
    """文件处理状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class BackupInfo:
    """备份文件信息"""
    path: Path
    name: str
    size: int
    size_str: str
    modified: datetime
    similarity: float
    file_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'path': str(self.path),
            'name': self.name,
            'size': self.size,
            'size_str': self.size_str,
            'modified': self.modified.isoformat(),
            'similarity': self.similarity,
            'file_type': self.file_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupInfo':
        """从字典创建"""
        return cls(
            path=Path(data['path']),
            name=data['name'],
            size=data['size'],
            size_str=data['size_str'],
            modified=datetime.fromisoformat(data['modified']),
            similarity=data['similarity'],
            file_type=data['file_type']
        )


@dataclass
class FileQueueItem:
    """文件队列项"""
    id: str
    name: str
    path: Optional[Path]
    size: int
    status: FileStatus
    progress: float = 0.0
    message: str = ""
    backup_files: List[BackupInfo] = field(default_factory=list)
    selected_backup: Optional[Path] = None
    added_time: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    
    def __post_init__(self):
        if self.added_time is None:
            self.added_time = datetime.now()
        if self.last_modified is None:
            self.last_modified = self.added_time
    
    def update_status(self, status: FileStatus, message: str = ""):
        """更新状态"""
        self.status = status
        self.message = message
        self.last_modified = datetime.now()
    
    def add_backup(self, backup_info: BackupInfo):
        """添加备份信息"""
        self.backup_files.append(backup_info)
        self.last_modified = datetime.now()
    
    def set_selected_backup(self, backup_path: Path):
        """设置选中的备份"""
        self.selected_backup = backup_path
        self.last_modified = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            'id': self.id,
            'name': self.name,
            'path': str(self.path) if self.path else None,
            'size': self.size,
            'status': self.status.value,
            'progress': self.progress,
            'message': self.message,
            'backup_files': [backup.to_dict() for backup in self.backup_files],
            'selected_backup': str(self.selected_backup) if self.selected_backup else None,
            'added_time': self.added_time.isoformat() if self.added_time else None,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileQueueItem':
        """从字典创建（用于反序列化）"""
        item = cls(
            id=data['id'],
            name=data['name'],
            path=Path(data['path']) if data['path'] else None,
            size=data['size'],
            status=FileStatus(data['status']),
            progress=data.get('progress', 0.0),
            message=data.get('message', ''),
            selected_backup=Path(data['selected_backup']) if data['selected_backup'] else None,
            added_time=datetime.fromisoformat(data['added_time']) if data['added_time'] else None,
            last_modified=datetime.fromisoformat(data['last_modified']) if data['last_modified'] else None
        )
        
        # 恢复备份文件列表
        item.backup_files = [
            BackupInfo.from_dict(backup_data) 
            for backup_data in data.get('backup_files', [])
        ]
        
        return item


class FileQueue:
    """文件队列管理器"""
    
    def __init__(self):
        self.items: List[FileQueueItem] = []
        self._stats = {
            'total': 0,
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'error': 0,
            'cancelled': 0
        }
    
    def add_item(self, item: FileQueueItem) -> bool:
        """添加文件项"""
        # 检查是否已存在
        if self.get_item(item.id):
            return False
        
        self.items.append(item)
        self._update_stats()
        return True
    
    def get_item(self, item_id: str) -> Optional[FileQueueItem]:
        """获取文件项"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def remove_item(self, item_id: str) -> bool:
        """移除文件项"""
        original_count = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]
        
        if len(self.items) < original_count:
            self._update_stats()
            return True
        return False
    
    def clear(self):
        """清空队列"""
        self.items.clear()
        self._update_stats()
    
    def get_items_by_status(self, status: FileStatus) -> List[FileQueueItem]:
        """按状态获取文件项"""
        return [item for item in self.items if item.status == status]
    
    def get_items_with_backups(self) -> List[FileQueueItem]:
        """获取有备份文件的项"""
        return [item for item in self.items if item.backup_files]
    
    def get_restorable_items(self) -> List[FileQueueItem]:
        """获取可恢复的文件项"""
        return [
            item for item in self.items 
            if item.backup_files and item.selected_backup
        ]
    
    def _update_stats(self):
        """更新统计信息"""
        self._stats = {
            'total': len(self.items),
            'pending': len(self.get_items_by_status(FileStatus.PENDING)),
            'processing': len(self.get_items_by_status(FileStatus.PROCESSING)),
            'completed': len(self.get_items_by_status(FileStatus.COMPLETED)),
            'error': len(self.get_items_by_status(FileStatus.ERROR)),
            'cancelled': len(self.get_items_by_status(FileStatus.CANCELLED))
        }
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        self._update_stats()
        return self._stats.copy()
    
    def get_total_size(self) -> int:
        """获取总文件大小"""
        return sum(item.size for item in self.items)
    
    def to_json(self) -> str:
        """导出为JSON"""
        data = {
            'items': [item.to_dict() for item in self.items],
            'stats': self.get_stats(),
            'exported_at': datetime.now().isoformat()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def from_json(self, json_str: str) -> bool:
        """从JSON导入"""
        try:
            data = json.loads(json_str)
            self.items = [
                FileQueueItem.from_dict(item_data) 
                for item_data in data.get('items', [])
            ]
            self._update_stats()
            return True
        except Exception:
            return False
    
    def save_to_file(self, file_path: Path) -> bool:
        """保存到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.to_json())
            return True
        except Exception:
            return False
    
    def load_from_file(self, file_path: Path) -> bool:
        """从文件加载"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return self.from_json(f.read())
        except Exception:
            return False
    
    def export_status_report(self) -> str:
        """导出状态报告"""
        lines = ["baku 文件队列状态报告", "=" * 40, ""]
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"总文件数: {len(self.items)}")
        
        stats = self.get_stats()
        lines.append("")
        lines.append("状态统计:")
        for status, count in stats.items():
            if status != 'total':
                lines.append(f"  {status}: {count}")
        
        lines.append("")
        lines.append("文件详情:")
        lines.append("-" * 40)
        
        for item in self.items:
            lines.append(f"文件: {item.name}")
            lines.append(f"  ID: {item.id}")
            lines.append(f"  状态: {item.status.value}")
            lines.append(f"  路径: {item.path or '未设置'}")
            lines.append(f"  大小: {self._format_file_size(item.size)}")
            lines.append(f"  消息: {item.message}")
            if item.backup_files:
                lines.append(f"  备份文件数: {len(item.backup_files)}")
                for backup in item.backup_files:
                    lines.append(f"    - {backup.name} ({backup.size_str})")
            lines.append(f"  添加时间: {item.added_time}")
            lines.append("")
        
        return "\n".join(lines)
    
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
    
    def get_status_stats(self) -> Dict[FileStatus, int]:
        """获取状态统计 - 返回每个状态的文件数量"""
        stats = {}
        for status in FileStatus:
            stats[status] = len([item for item in self.items if item.status == status])
        return stats
