"""
BakR - 备份文件恢复工具
基于 PyTauri 的现代化桌面应用
"""
import asyncio
from pathlib import Path
from typing import Dict, Any, List
import json
import sys
import os

# 模拟 PyTapytauri 实际使用时需要安装 pytauri）
try:
    from pytauri import App, Window, invoke, Manager
    TAURI_AVAILABLE = True
except ImportError:
    # 如果没有安装 pytauri，使用模拟类
    print("PyTauri not installed, using mock implementation")
    TAURI_AVAILABLE = False
    
    class Manager:
        def __init__(self):
            self.windows = {}
        
        def get_window(self, label):
            return MockWindow()
    
    class MockWindow:
        def emit(self, event, data):
            print(f"Event: {event}, Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    class App:
        def __init__(self, manager=None):
            self.manager = manager or Manager()
        
        def run(self):
            print("BakR application started (mock mode)")
            print("请安装 pytauri 以获得完整功能")
            print("前端界面位于: ui/index.html")
            
            # 在浏览器中打开前端
            ui_path = Path(__file__).parent.parent / "ui" / "index.html"
            if ui_path.exists():
                import webbrowser
                webbrowser.open(f"file:///{ui_path.resolve()}")
                print(f"已在浏览器中打开: {ui_path}")
            
            # 模拟运行
            import time
            try:
                print("按 Ctrl+C 退出...")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n应用退出")
    
    def invoke(func):
        return func

from backup_finder import BackupFinder
from backup_restorer import BackupRestorer


class BakRApp:
    """BakR 主应用类"""
    
    def __init__(self):
        self.finder = BackupFinder()
        self.restorer = BackupRestorer()
        self.operation_history = []
        
        # 初始化 Tauri
        if TAURI_AVAILABLE:
            self.manager = Manager()
            self.app = App(self.manager)
        else:
            self.manager = Manager()
            self.app = App()
    
    def get_window(self):
        """获取主窗口"""
        return self.manager.get_window("main")
    
    def emit_event(self, event: str, data: Any):
        """发送事件到前端"""
        window = self.get_window()
        if window:
            window.emit(event, data)
    
    @invoke
    async def find_backup(self, file_path: str) -> Dict[str, Any]:
        """查找备份文件"""
        try:
            self.emit_event("log", {"type": "info", "message": f"开始查找备份文件: {file_path}"})
            
            target_file = Path(file_path)
            
            if not target_file.exists():
                result = {
                    "success": False,
                    "message": f"文件不存在: {file_path}",
                    "data": None
                }
                self.emit_event("log", {"type": "error", "message": result["message"]})
                return result
            
            backup_file = self.finder.find_nearest_backup(target_file)
            search_info = self.finder.get_search_info(target_file)
            
            if backup_file:
                preview = self.restorer.preview_restore(target_file, backup_file)
                result = {
                    "success": True,
                    "message": f"找到备份文件: {backup_file}",
                    "data": {
                        "backup_found": True,
                        "backup_file": str(backup_file),
                        "search_info": search_info,
                        "preview": preview
                    }
                }
                self.emit_event("log", {"type": "success", "message": result["message"]})
            else:
                result = {
                    "success": True,
                    "message": "未找到对应的备份文件",
                    "data": {
                        "backup_found": False,
                        "backup_file": None,
                        "search_info": search_info,
                        "preview": None
                    }
                }
                self.emit_event("log", {"type": "warning", "message": result["message"]})
            
            return result
                
        except Exception as e:
            result = {
                "success": False,
                "message": f"查找失败: {str(e)}",
                "data": None
            }
            self.emit_event("log", {"type": "error", "message": result["message"]})
            return result
    
    @invoke
    async def restore_backup(self, target_file_path: str, backup_file_path: str) -> Dict[str, Any]:
        """执行备份恢复"""
        try:
            self.emit_event("log", {"type": "info", "message": f"开始恢复: {backup_file_path} -> {target_file_path}"})
            
            target_file = Path(target_file_path)
            backup_file = Path(backup_file_path)
            
            result = self.restorer.restore_backup(target_file, backup_file)
            
            # 记录操作历史
            if result["success"]:
                self.operation_history.append({
                    "timestamp": result["details"]["timestamp"],
                    "operation": "restore",
                    "target_file": target_file_path,
                    "backup_file": backup_file_path,
                    "success": True
                })
                self.emit_event("log", {"type": "success", "message": result["message"]})
                self.emit_event("restore_complete", result)
            else:
                self.emit_event("log", {"type": "error", "message": result["message"]})
            
            return result
            
        except Exception as e:
            result = {
                "success": False,
                "message": f"恢复失败: {str(e)}",
                "details": {"error": str(e)}
            }
            self.emit_event("log", {"type": "error", "message": result["message"]})
            return result
    
    @invoke
    async def preview_restore(self, target_file_path: str, backup_file_path: str) -> Dict[str, Any]:
        """预览恢复操作"""
        try:
            target_file = Path(target_file_path)
            backup_file = Path(backup_file_path)
            
            preview = self.restorer.preview_restore(target_file, backup_file)
            
            return {
                "success": True,
                "message": "预览生成成功",
                "data": preview
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"预览失败: {str(e)}",
                "data": None
            }
    
    @invoke
    async def get_operation_history(self) -> List[Dict[str, Any]]:
        """获取操作历史"""
        return self.operation_history
    
    @invoke
    async def clear_operation_history(self) -> Dict[str, Any]:
        """清空操作历史"""
        self.operation_history.clear()
        self.emit_event("log", {"type": "info", "message": "操作历史已清空"})
        return {"success": True, "message": "操作历史已清空"}
    
    @invoke
    async def get_app_info(self) -> Dict[str, Any]:
        """获取应用信息"""
        return {
            "name": "BakR",
            "version": "0.1.0",
            "description": "智能备份文件恢复工具",
            "supported_extensions": [".bak", ".backup", ".old"],
            "tauri_available": TAURI_AVAILABLE
        }
    
    def run(self):
        """运行应用"""
        try:
            print("=" * 60)
            print("🚀 启动 BakR 应用...")
            print("📁 智能备份文件恢复工具")
            print("=" * 60)
            print()
            print("功能说明:")
            print("- 🎯 拖拽文件到应用窗口")
            print("- 🔍 自动查找对应的 .bak/.backup/.old 文件")
            print("- 👀 预览恢复操作")
            print("- 🔄 执行恢复（原文件备份为 .new）")
            print("- 📝 记录操作历史")
            print()
            
            if TAURI_AVAILABLE:
                print("✅ PyTauri 可用，启动完整桌面应用")
            else:
                print("⚠️  PyTauri 不可用，使用演示模式")
                print("💡 安装 PyTauri: pip install pytauri")
                print()
            
            # 发送初始化事件
            self.emit_event("app_ready", {
                "message": "应用初始化完成",
                "tauri_available": TAURI_AVAILABLE
            })
            
            self.app.run()
            
        except KeyboardInterrupt:
            print("\n👋 应用被用户中断")
        except Exception as e:
            print(f"❌ 应用运行出错: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    app = BakRApp()
    app.run()


if __name__ == "__main__":
    main()
