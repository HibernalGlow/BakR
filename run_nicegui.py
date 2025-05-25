#!/usr/bin/env python3
"""
BakR NiceGUI 应用启动器
"""
import sys
import os
from pathlib import Path

# 添加 src 目录到 Python 路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from nicegui_app import main
    
    print("🚀 启动 BakR NiceGUI 应用...")
    print("📍 应用将在浏览器中打开: http://localhost:8080")
    
    # 启动 NiceGUI 应用
    main()
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("💡 请先安装 NiceGUI: pip install nicegui>=1.4.0")
    sys.exit(1)
except Exception as e:
    print(f"❌ 启动失败: {e}")
    sys.exit(1)
