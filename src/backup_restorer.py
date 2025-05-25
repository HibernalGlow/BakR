"""
备份恢复器模块
负责执行备份恢复操作
"""
import shutil
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from datetime import datetime


class BackupRestorer:
    """备份恢复操作类"""
    
    def restore_backup(self, target_file: Path, backup_file: Path) -> Dict[str, Any]:
        """
        恢复备份文件
        1. 将原文件重命名为 .new
        2. 将备份文件复制到原位置
        """
        try:
            # 检查文件是否存在
            if not backup_file.exists():
                return {
                    "success": False,
                    "message": f"备份文件不存在: {backup_file}",
                    "details": {}
                }
            
            new_file_path = None
            
            # 如果目标文件存在，先备份为 .new
            if target_file.exists():
                new_file_path = self._create_new_backup(target_file)
                if not new_file_path:
                    return {
                        "success": False,
                        "message": "无法创建 .new 备份文件",
                        "details": {}
                    }
            
            # 复制备份文件到目标位置
            shutil.copy2(backup_file, target_file)
            
            return {
                "success": True,
                "message": f"成功恢复 {backup_file.name} 到 {target_file.name}",
                "details": {
                    "target_file": str(target_file),
                    "backup_file": str(backup_file),
                    "new_file": str(new_file_path) if new_file_path else None,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"恢复失败: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _create_new_backup(self, target_file: Path) -> Optional[Path]:
        """创建 .new 备份文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file = target_file.with_suffix(f"{target_file.suffix}.new")
            
            # 如果 .new 文件已存在，添加时间戳
            if new_file.exists():
                new_file = target_file.with_suffix(f"{target_file.suffix}.new.{timestamp}")
            
            shutil.copy2(target_file, new_file)
            return new_file
            
        except Exception:
            return None
    
    def preview_restore(self, target_file: Path, backup_file: Path) -> Dict[str, Any]:
        """预览恢复操作，不实际执行"""
        target_exists = target_file.exists()
        backup_exists = backup_file.exists()
        
        new_file_path = None
        if target_exists:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file_path = target_file.with_suffix(f"{target_file.suffix}.new")
            if new_file_path.exists():
                new_file_path = target_file.with_suffix(f"{target_file.suffix}.new.{timestamp}")
        
        return {
            "target_file": {
                "path": str(target_file),
                "exists": target_exists,
                "size": target_file.stat().st_size if target_exists else 0,
                "modified": datetime.fromtimestamp(target_file.stat().st_mtime).isoformat() if target_exists else None
            },
            "backup_file": {
                "path": str(backup_file),
                "exists": backup_exists,
                "size": backup_file.stat().st_size if backup_exists else 0,
                "modified": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat() if backup_exists else None
            },
            "new_file": {
                "path": str(new_file_path) if new_file_path else None,
                "will_create": target_exists
            },
            "can_restore": backup_exists
        }
