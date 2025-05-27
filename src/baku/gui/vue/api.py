"""
BakU Vue GUI Backend API
为 Vue 前端提供 Python 后端接口
"""
import json
import os
import sys
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from baku.core.backup_finder import BackupFinder
from baku.core.backup_restorer import BackupRestorer
from baku.core.file_queue import FileQueue, FileStatus


class BakUAPI:
    """BakU 后端 API 类"""
    
    def __init__(self):
        self.backup_finder = BackupFinder()
        self.backup_restorer = BackupRestorer()
        self.file_queue = FileQueue()
        self.js_callback = None
        
    def set_js_callback(self, callback):
        """设置 JavaScript 回调函数"""
        self.js_callback = callback
        
    def log(self, message: str, level: str = 'info'):
        """发送日志到前端"""
        if self.js_callback:
            try:
                self.js_callback.call('addLog', message, level)
            except Exception as e:
                print(f"日志发送失败: {e}")
        else:
            print(f"[{level.upper()}] {message}")
    
    def scan_backups(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        扫描文件的备份
        
        Args:
            file_paths: 要扫描的文件路径列表
            
        Returns:
            扫描结果列表，每个项目包含:
            - backup_found: bool 是否找到备份
            - backup_path: str 备份路径（如果找到）
            - message: str 结果消息
        """
        results = []
        
        try:
            self.log(f"开始扫描 {len(file_paths)} 个文件的备份...")
            
            for i, file_path in enumerate(file_paths):
                try:
                    self.log(f"扫描 {os.path.basename(file_path)}...")
                    
                    # 查找备份
                    backup_files = self.backup_finder.find_backups(file_path)
                    
                    if backup_files:
                        # 找到备份，选择最新的
                        latest_backup = max(backup_files, key=lambda x: x.get('timestamp', 0))
                        results.append({
                            'backup_found': True,
                            'backup_path': latest_backup['path'],
                            'message': f"找到备份: {latest_backup['path']}"
                        })
                        self.log(f"✓ {os.path.basename(file_path)} 找到备份", 'success')
                    else:
                        results.append({
                            'backup_found': False,
                            'backup_path': None,
                            'message': '未找到备份文件'
                        })
                        self.log(f"⚠ {os.path.basename(file_path)} 未找到备份", 'warning')
                        
                except Exception as e:
                    error_msg = f"扫描失败: {str(e)}"
                    results.append({
                        'backup_found': False,
                        'backup_path': None,
                        'message': error_msg
                    })
                    self.log(f"✗ {os.path.basename(file_path)} 扫描失败: {error_msg}", 'error')
            
            found_count = sum(1 for r in results if r['backup_found'])
            self.log(f"扫描完成！找到 {found_count}/{len(file_paths)} 个备份", 'success')
            
        except Exception as e:
            self.log(f"扫描过程发生错误: {str(e)}", 'error')
            traceback.print_exc()
            
        return results
    
    def restore_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        恢复文件
        
        Args:
            file_paths: 要恢复的文件路径列表
            
        Returns:
            恢复结果列表，每个项目包含:
            - success: bool 是否成功
            - message: str 结果消息
            - restored_path: str 恢复后的路径（如果成功）
        """
        results = []
        
        try:
            self.log(f"开始恢复 {len(file_paths)} 个文件...")
            
            for i, file_path in enumerate(file_paths):
                try:
                    self.log(f"恢复 {os.path.basename(file_path)}...")
                    
                    # 先查找备份
                    backup_files = self.backup_finder.find_backups(file_path)
                    
                    if not backup_files:
                        error_msg = "未找到备份文件"
                        results.append({
                            'success': False,
                            'message': error_msg,
                            'restored_path': None
                        })
                        self.log(f"✗ {os.path.basename(file_path)} {error_msg}", 'error')
                        continue
                    
                    # 选择最新的备份
                    latest_backup = max(backup_files, key=lambda x: x.get('timestamp', 0))
                    backup_path = latest_backup['path']
                    
                    # 执行恢复
                    success = self.backup_restorer.restore_file(backup_path, file_path)
                    
                    if success:
                        results.append({
                            'success': True,
                            'message': f"恢复成功 <- {backup_path}",
                            'restored_path': file_path
                        })
                        self.log(f"✓ {os.path.basename(file_path)} 恢复成功", 'success')
                    else:
                        error_msg = "恢复失败"
                        results.append({
                            'success': False,
                            'message': error_msg,
                            'restored_path': None
                        })
                        self.log(f"✗ {os.path.basename(file_path)} {error_msg}", 'error')
                        
                except Exception as e:
                    error_msg = f"恢复失败: {str(e)}"
                    results.append({
                        'success': False,
                        'message': error_msg,
                        'restored_path': None
                    })
                    self.log(f"✗ {os.path.basename(file_path)} 恢复失败: {error_msg}", 'error')
            
            success_count = sum(1 for r in results if r['success'])
            self.log(f"恢复完成！成功: {success_count}/{len(file_paths)}", 'success')
            
        except Exception as e:
            self.log(f"恢复过程发生错误: {str(e)}", 'error')
            traceback.print_exc()
            
        return results
    
    def process_files(self, files: List[Dict], auto_mode: bool = True) -> Dict[str, Any]:
        """
        处理拖拽的文件
        
        Args:
            files: 文件列表，每个文件包含 name, path 等信息
            auto_mode: 是否自动模式
            
        Returns:
            处理结果
        """
        try:
            file_paths = []
            
            # 提取文件路径
            for file in files:
                if isinstance(file, dict):
                    path = file.get('path') or file.get('name', '')
                elif hasattr(file, 'path'):
                    path = file.path
                elif hasattr(file, 'name'):
                    path = file.name
                else:
                    path = str(file)
                
                if path:
                    file_paths.append(path)
            
            self.log(f"接收到 {len(file_paths)} 个文件")
            
            if auto_mode:
                # 自动模式：直接恢复
                self.log("自动模式：开始恢复文件...", 'info')
                results = self.restore_files(file_paths)
                return {'status': 'completed', 'results': results}
            else:
                # 手动模式：添加到队列
                self.log("手动模式：文件已添加到队列", 'info')
                return {'status': 'queued', 'files': file_paths}
                
        except Exception as e:
            error_msg = f"处理文件失败: {str(e)}"
            self.log(error_msg, 'error')
            traceback.print_exc()
            return {'status': 'error', 'message': error_msg}
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置信息"""
        try:
            return {
                'backup_locations': self.backup_finder.backup_locations,
                'file_patterns': self.backup_finder.file_patterns,
                'max_depth': getattr(self.backup_finder, 'max_depth', 3)
            }
        except Exception as e:
            self.log(f"获取配置失败: {str(e)}", 'error')
            return {}
    
    def set_config(self, config: Dict[str, Any]) -> bool:
        """设置配置信息"""
        try:
            if 'backup_locations' in config:
                self.backup_finder.backup_locations = config['backup_locations']
            if 'file_patterns' in config:
                self.backup_finder.file_patterns = config['file_patterns']
            if 'max_depth' in config:
                self.backup_finder.max_depth = config['max_depth']
            
            self.log("配置更新成功", 'success')
            return True
        except Exception as e:
            self.log(f"配置更新失败: {str(e)}", 'error')
            return False


# 全局 API 实例
api = BakUAPI()


def get_api():
    """获取 API 实例"""
    return api
