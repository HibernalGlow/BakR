#!/usr/bin/env python3
"""
BakU GUI 启动脚本 - ttkbootstrap 版本
"""

if __name__ == "__main__":
    from tkinterdnd2 import TkinterDnD
    from baku.gui.ttkb import BakUGUI
    
    root = TkinterDnD.Tk()
    app = BakUGUI(root)
    
    print("BakU GUI 启动中...")
    print("功能特性：")
    print("- 全主题化界面（使用 ttkbootstrap）")
    print("- 可编辑队列（多选、右键菜单）")
    print("- 自动/手动模式切换")
    print("- 实时日志显示")
    print("- 拖拽文件支持")
    
    root.mainloop()
