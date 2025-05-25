"""
备份文件查找器模块
负责查找最近的 .bak 文件
"""
import os
from pathlib import Path
from typing import Optional, List
from loguru import logger


class BackupFinder:
    """查找备份文件的核心类"""
    
    def __init__(self):
        self.search_extensions = ['.bak', '.backup', '.old']
    
    def find_nearest_backup(self, target_file: Path) -> Optional[Path]:
        """
        查找最近的备份文件
        首先在同级目录查找，然后向上级目录查找
        """
        target_name = target_file.name
        current_dir = target_file.parent
        
        # 先在同级目录查找
        backup_file = self._search_in_directory(current_dir, target_name)
        if backup_file:
            return backup_file
        
        # 向上级目录查找
        return self._search_parent_directories(current_dir, target_name)
    
    def _search_in_directory(self, directory: Path, target_name: str) -> Optional[Path]:
        """在指定目录中查找备份文件"""
        for ext in self.search_extensions:
            backup_path = directory / f"{target_name}{ext}"
            if backup_path.exists():
                return backup_path
        return None
    
    def _search_parent_directories(self, start_dir: Path, target_name: str) -> Optional[Path]:
        """向上级目录递归查找"""
        current = start_dir.parent
        
        while current != current.parent:  # 直到根目录
            backup_file = self._search_in_directory(current, target_name)
            if backup_file:
                return backup_file
            current = current.parent
        
        return None

    def get_search_info(self, target_file: Path) -> dict:
        """获取搜索信息，用于前端显示"""
        target_name = target_file.name
        current_dir = target_file.parent
        
        search_paths = []
        
        # 同级目录
        for ext in self.search_extensions:
            search_paths.append({
                "path": str(current_dir / f"{target_name}{ext}"),
                "level": "同级目录",
                "exists": (current_dir / f"{target_name}{ext}").exists()
            })
        
        # 上级目录
        parent = current_dir.parent
        level = 1
        while parent != parent.parent and level <= 5:  # 最多查找5级
            for ext in self.search_extensions:
                backup_path = parent / f"{target_name}{ext}"
                search_paths.append({
                    "path": str(backup_path),
                    "level": f"上级目录 {level}",
                    "exists": backup_path.exists()
                })
            parent = parent.parent
            level += 1
        
        return {
            "target_file": str(target_file),
            "search_paths": search_paths
        }
