import ttkbootstrap as tb
from ttkbootstrap.constants import *
import re
from datetime import datetime

class LogPanel(tb.Frame):
    def __init__(self, master, style):
        super().__init__(master, bootstyle="dark")
        self.style = style
          # 日志文本框
        self.text = tb.Text(
            self, 
            height=15, 
            font=("Consolas", 9), 
            wrap="word"
        )
          # 滚动条
        scrollbar = tb.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.text.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
          # 清空按钮
        clear_frame = tb.Frame(self)
        clear_frame.pack(side=BOTTOM, fill=X, pady=(5, 0))
        
        tb.Button(
            clear_frame, 
            text="🗑️ 清空日志", 
            command=self.clear_log, 
            bootstyle="outline-danger",
            width=12
        ).pack()
        
        self.setup_theme_colors()
    
    def setup_theme_colors(self):
        """设置主题色标签"""
        try:
            # 使用 style.lookup 获取主题色
            primary_color = self.style.lookup("TLabel", "foreground") or "#007bff"
            success_color = self.style.lookup("success.TLabel", "foreground") or "#28a745"
            danger_color = self.style.lookup("danger.TLabel", "foreground") or "#dc3545"
            warning_color = self.style.lookup("warning.TLabel", "foreground") or "#ffc107"
            info_color = self.style.lookup("info.TLabel", "foreground") or "#17a2b8"
            
            # 配置日志标签颜色
            self.text.tag_configure("INFO", foreground=info_color)
            self.text.tag_configure("SUCCESS", foreground=success_color)
            self.text.tag_configure("ERROR", foreground=danger_color)
            self.text.tag_configure("WARNING", foreground=warning_color)
            self.text.tag_configure("DEFAULT", foreground=primary_color)
            self.text.tag_configure("TIME", foreground="#888888", font=("Consolas", 8))
            
        except Exception as e:
            # 备用颜色方案
            self.text.tag_configure("INFO", foreground="#17a2b8")
            self.text.tag_configure("SUCCESS", foreground="#28a745")
            self.text.tag_configure("ERROR", foreground="#dc3545")
            self.text.tag_configure("WARNING", foreground="#ffc107")
            self.text.tag_configure("DEFAULT", foreground="#ffffff")
            self.text.tag_configure("TIME", foreground="#888888")
    
    def update_theme_colors(self):
        """主题切换时更新颜色"""
        self.setup_theme_colors()
    
    def log(self, msg, tag="INFO"):
        """添加日志消息"""
        # 添加时间戳
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 自动检测消息类型
        if tag == "INFO":
            text = str(msg)
            if re.search(r"成功|✓|✔", text):
                tag = "SUCCESS"
            elif re.search(r"错误|失败|✗|❌", text):
                tag = "ERROR"
            elif re.search(r"警告|⚠", text):
                tag = "WARNING"
        
        # 插入时间戳
        self.text.insert(END, f"[{timestamp}] ", "TIME")
        # 插入消息
        self.text.insert(END, str(msg) + "\n", tag)
        # 自动滚动到底部
        self.text.see(END)
    
    def clear_log(self):
        """清空日志"""
        self.text.delete(1.0, END)
        self.log("日志已清空", "INFO")