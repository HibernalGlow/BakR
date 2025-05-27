#!/usr/bin/env python3
"""
BakUI 主模块 - 启动图形界面
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from .ui_main import start_ui

if __name__ == "__main__":
    start_ui()
