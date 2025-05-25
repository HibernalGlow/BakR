import customtkinter as ctk
import tkinter as tk

class ScanPanel(ctk.CTkFrame):
    def __init__(self, master, theme=None):
        super().__init__(master)
        self.theme = theme or {}
        self._create_widgets()

    def _create_widgets(self):
        label = ctk.CTkLabel(self, text="扫描备份区", font=("微软雅黑", 18), text_color=self.theme.get("fg", None), bg_color=self.theme.get("bg", None))
        label.pack(pady=20)
        # TODO: 添加扫描按钮、进度条等 