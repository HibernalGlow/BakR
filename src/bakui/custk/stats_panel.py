import customtkinter as ctk
import tkinter as tk

class StatsPanel(ctk.CTkFrame):
    def __init__(self, master, theme=None):
        super().__init__(master)
        self.theme = theme or {}
        self._create_widgets()

    def _create_widgets(self):
        label = ctk.CTkLabel(self, text="统计信息区", font=("微软雅黑", 18), text_color=self.theme.get("fg", None), bg_color=self.theme.get("bg", None))
        label.pack(pady=20)
        # TODO: 添加统计信息展示 