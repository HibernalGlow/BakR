"""
备份文件查找器模块
负责查找最近的 .bak 文件
"""
import os
from pathlib import Path
from typing import Optional, List
from loguru import logger
from bakr.config.config import load_bakr_config


class BackupFinder:
    """查找备份文件的核心类"""
    
    def __init__(self):
        config = load_bakr_config()
        self.search_extensions = config.get('bak_extensions', ['.bak', '.backup', '.old'])
        self.max_recurse_level = config.get('max_recurse_level', 5)
    
    def find_nearest_backup(self, target_file: Path) -> Optional[Path]:
        """
        1. 先查找同目录同名备份
        2. 没有则回溯向上查找任意bak文件（不要求同名）
        """
        target_name = target_file.name
        current_dir = target_file.parent
        tried_paths = []
        # Step 1: 同目录同名
        for ext in self.search_extensions:
            path = current_dir / f"{target_name}{ext}"
            tried_paths.append(str(path))
            if path.exists():
                logger.info(f"同目录同名备份命中: {path}")
                logger.debug(f"查找路径: {tried_paths}")
                return path
        # Step 2: 回溯向上找任意bak
        parent = current_dir
        for level in range(self.max_recurse_level):
            for file in parent.iterdir():
                if file.is_file() and file.suffix in self.search_extensions:
                    tried_paths.append(str(file))
                    logger.info(f"回溯模式命中: {file} (level={level+1})")
                    logger.debug(f"查找路径: {tried_paths}")
                    return file
            if parent == parent.parent:
                break
            parent = parent.parent
        logger.warning(f"未找到备份文件，已查找路径: {tried_paths}")
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
