#!/usr/bin/env python3
"""
BakU Flet UI 快速启动脚本
"""
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bakui.fletui.flet_app import main

if __name__ == "__main__":
    main()
