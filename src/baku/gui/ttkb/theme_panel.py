import ttkbootstrap as tb
from ttkbootstrap.constants import *

class ThemePanel(tb.Frame):
    def __init__(self, master, main_app):
        super().__init__(master, bootstyle="info")
        self.main_app = main_app
        
        tb.Label(self, text="🎨 主题:", bootstyle="info").pack(side=LEFT, padx=(0, 5))
        
        # 主题选择下拉菜单
        self.theme_var = tb.StringVar(value=self.main_app.style.theme_use())
        theme_menu = tb.OptionMenu(
            self, 
            self.theme_var, 
            self.main_app.style.theme_use(), 
            *self.main_app.style.theme_names(), 
            command=self.change_theme,
            bootstyle="info"
        )
        theme_menu.pack(side=LEFT, padx=(0, 10))
        
        # 快速主题按钮
        popular_themes = ["litera","superhero", "darkly", "solar", "flatly", "cosmo"]
        for theme in popular_themes:
            if theme in self.main_app.style.theme_names():
                btn = tb.Button(
                    self, 
                    text=theme.title(), 
                    bootstyle="outline-secondary",
                    command=lambda t=theme: self.quick_change_theme(t),
                    width=8
                )
                btn.pack(side=LEFT, padx=2)
    
    def change_theme(self, theme):
        """通过下拉菜单切换主题"""
        self.main_app.change_theme(theme)
    
    def quick_change_theme(self, theme):
        """快速切换主题按钮"""
        self.theme_var.set(theme)
        self.main_app.change_theme(theme)