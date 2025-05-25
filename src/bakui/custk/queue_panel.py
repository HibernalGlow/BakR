import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

class QueuePanel(ctk.CTkFrame):
    def __init__(self, master, theme=None):
        super().__init__(master)
        self.theme = theme or {}
        self.file_list = []
        self._create_widgets()

    def _create_widgets(self):
        label = ctk.CTkLabel(self, text="文件队列管理区", font=("微软雅黑", 18), text_color=self.theme.get("fg", None), bg_color=self.theme.get("bg", None))
        label.pack(pady=20)
        btn_add = ctk.CTkButton(self, text="添加文件", command=self.add_files,
            fg_color=self.theme.get("accent", None),
            hover_color=self.theme.get("button_hover", None),
            text_color=self.theme.get("bg", None),
            font=("微软雅黑", 14))
        btn_add.pack(pady=10)
        self.listbox = tk.Listbox(self, selectmode=tk.EXTENDED, bg=self.theme.get("bg", "#222"), fg=self.theme.get("fg", "#fff"),
                                  highlightbackground=self.theme.get("border", "#444"), relief=tk.FLAT, font=("Consolas", 12), width=60, height=12)
        self.listbox.pack(pady=10)
        # 拖拽支持（预留接口）
        # self.listbox.drop_target_register('DND_Files')
        # self.listbox.dnd_bind('<<Drop>>', self.on_drop_files)

    def add_files(self):
        files = filedialog.askopenfilenames(title="选择文件", filetypes=[("所有文件", "*.*")])
        for f in files:
            if f not in self.file_list:
                self.file_list.append(f)
                self.listbox.insert(tk.END, f)

    def on_drop_files(self, event):
        files = self.tk.splitlist(event.data)
        for f in files:
            if f not in self.file_list:
                self.file_list.append(f)
                self.listbox.insert(tk.END, f) 