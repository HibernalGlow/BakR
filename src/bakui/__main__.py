#!/usr/bin/env python3
"""
BakUI 主模块 - 启动图形界面
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from bakui.fletui.flet_app import main

if __name__ == "__main__":
    main()
