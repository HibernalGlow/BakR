#!/usr/bin/env python3
"""
BakR 启动脚本
自动检测 PyTauri 并启动相应模式
"""
import sys
import os
import webbrowser
from pathlib import Path
import time


def check_pytauri():
    """检查 PyTauri 是否可用"""
    try:
        import pytauri
        # 尝试实际使用 pytauri 的一个简单功能来验证
        pytauri.api
        return True
    except (ImportError, RuntimeError, AttributeError) as e:
        print(f"PyTauri 检查失败: {e}")
        return False


def start_gui_mode():
    """启动桌面 GUI 模式"""
    print("🚀 启动桌面 GUI 模式...")
    
    # 导入并运行主应用
    from src.main import main
    main()


def start_web_mode():
    """启动 Web 演示模式"""
    print("🌐 启动 Web 演示模式...")
    
    # 找到 HTML 文件
    ui_path = Path(__file__).parent / "ui" / "index.html"
    
    if ui_path.exists():
        # 在浏览器中打开 UI
        url = f"file:///{ui_path.resolve()}"
        print(f"📂 在浏览器中打开: {url}")
        webbrowser.open(url)
        
        print("\n" + "="*60)
        print("💡 BakR Web 演示模式已启动")
        print("="*60)
        print()
        print("功能说明:")
        print("- 🎯 在页面中可以体验界面功能")
        print("- 📱 当前为演示模式，部分功能受限")
        print("- 💻 要获得完整功能，请安装 PyTauri:")
        print("  pip install pytauri")
        print()
        print("🔄 安装完成后重新运行此脚本即可启用桌面模式")
        print()
        print("按 Ctrl+C 退出...")
        
        try:
            # 保持脚本运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 退出演示模式")
            
    else:
        print(f"❌ 找不到 UI 文件: {ui_path}")
        print("请确保项目文件完整")


def main():
    """主入口函数"""
    print("BakR - 智能备份文件恢复工具")
    print("="*50)
    
    # 检查 PyTauri 可用性
    if check_pytauri():
        print("✅ PyTauri 可用，启动完整桌面应用")
        start_gui_mode()
    else:
        print("⚠️  PyTauri 不可用，启动 Web 演示模式")
        print("💡 安装 PyTauri: pip install pytauri")
        print()
        start_web_mode()


if __name__ == "__main__":
    main()
