#!/usr/bin/env python3
"""
BakU Vue GUI 启动脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    from baku.gui.vue.main import main
    
    if __name__ == '__main__':
        print("🎯 启动 BakU Vue 界面...")
        main()
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所需依赖:")
    print("pip install pywebview>=5.0.0")
    sys.exit(1)
except Exception as e:
    print(f"❌ 启动失败: {e}")
    sys.exit(1)
