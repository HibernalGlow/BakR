#!/usr/bin/env python3
"""
BakR Streamlit Web应用启动脚本
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    import streamlit.web.cli as stcli
    
    # Streamlit应用文件路径
    app_file = project_root / "src" / "web" / "streamlit_app.py"
    
    # 设置Streamlit参数
    sys.argv = [
        "streamlit",
        "run",
        str(app_file),
        "--server.port=1942",
        "--server.address=localhost",
        "--server.headless=false",
        "--browser.gatherUsageStats=false",
        "--theme.base=light"
    ]
    
    stcli.main()
if __name__ == "__main__":
    main()