import customtkinter as ctk
import tkinter as tk
from bakui.custk.queue_panel import QueuePanel
from bakui.custk.scan_panel import ScanPanel
from bakui.custk.restore_panel import RestorePanel
from bakui.custk.stats_panel import StatsPanel

# Tokyonight主题主色
TOKYONIGHT_THEME = {
    "bg": "#1a1b26",
    "fg": "#c0caf5",
    "accent": "#7aa2f7",
    "button": "#414868",
    "button_hover": "#7aa2f7",
    "border": "#3b4261"
}

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.configure(bg=TOKYONIGHT_THEME["bg"])
        self.title("baku 智能备份恢复工具 - GUI")
        self.geometry("900x600")
        self.resizable(False, False)
        self._create_widgets()

    def _create_widgets(self):
        # 左侧导航栏
        self.nav_frame = ctk.CTkFrame(self, width=180, fg_color=TOKYONIGHT_THEME["bg"])
        self.nav_frame.pack(side="left", fill="y")
        btn_style = dict(
            fg_color=TOKYONIGHT_THEME["button"],
            hover_color=TOKYONIGHT_THEME["button_hover"],
            text_color=TOKYONIGHT_THEME["fg"],
            font=("微软雅黑", 15)
        )
        self.btn_queue = ctk.CTkButton(self.nav_frame, text="文件队列", command=self.show_queue, **btn_style)
        self.btn_scan = ctk.CTkButton(self.nav_frame, text="扫描备份", command=self.show_scan, **btn_style)
        self.btn_restore = ctk.CTkButton(self.nav_frame, text="恢复文件", command=self.show_restore, **btn_style)
        self.btn_stats = ctk.CTkButton(self.nav_frame, text="统计信息", command=self.show_stats, **btn_style)
        self.btn_queue.pack(pady=20, fill="x")
        self.btn_scan.pack(pady=20, fill="x")
        self.btn_restore.pack(pady=20, fill="x")
        self.btn_stats.pack(pady=20, fill="x")
        # 右侧主内容区
        self.content_frame = ctk.CTkFrame(self, fg_color=TOKYONIGHT_THEME["bg"])
        self.content_frame.pack(side="right", fill="both", expand=True)
        self.panels = {
            'queue': QueuePanel(self.content_frame, theme=TOKYONIGHT_THEME),
            'scan': ScanPanel(self.content_frame, theme=TOKYONIGHT_THEME),
            'restore': RestorePanel(self.content_frame, theme=TOKYONIGHT_THEME),
            'stats': StatsPanel(self.content_frame, theme=TOKYONIGHT_THEME)
        }
        self.current_panel = None
        self.show_queue()

    def show_panel(self, name):
        if self.current_panel:
            self.current_panel.pack_forget()
        panel = self.panels[name]
        panel.pack(fill="both", expand=True)
        self.current_panel = panel

    def show_queue(self):
        self.show_panel('queue')
    def show_scan(self):
        self.show_panel('scan')
    def show_restore(self):
        self.show_panel('restore')
    def show_stats(self):
        self.show_panel('stats')

def main():
    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main() 