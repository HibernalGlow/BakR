"""
BakU Vue GUI 主程序
使用 pywebview 启动 Vue 前端界面
"""
import os
import sys
import webbrowser
from pathlib import Path

import webview

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from baku.gui.vue.api import get_api


class BakUVueApp:
    """BakU Vue 应用程序"""
    
    def __init__(self):
        self.api = get_api()
        self.window = None
        
    def setup_api_bridge(self):
        """设置 API 桥接"""
        # 将 API 方法暴露给前端
        webview.expose(self.api.scan_backups)
        webview.expose(self.api.restore_files)
        webview.expose(self.api.process_files)
        webview.expose(self.api.get_config)
        webview.expose(self.api.set_config)
        
    def on_window_loaded(self):
        """窗口加载完成回调"""
        print("BakU Vue 界面加载完成")
        
        # 设置 JavaScript 回调
        try:
            self.api.set_js_callback(self.window.evaluate_js)
            self.api.log("BakU Vue 后端连接成功", "success")
        except Exception as e:
            print(f"设置 JS 回调失败: {e}")
    
    def run(self, dev_mode=False):
        """运行应用程序"""
        # 设置 API 桥接
        self.setup_api_bridge()
        
        if dev_mode:
            # 开发模式：连接到 Vite 开发服务器
            url = 'http://localhost:5173'
            print(f"开发模式：连接到 {url}")
            print("请确保已运行 'npm run dev' 启动开发服务器")
        else:
            # 生产模式：使用构建后的文件
            vue_dist = Path(__file__).parent / "dist"
            if not vue_dist.exists():
                print("错误：未找到构建后的文件")
                print("请先运行 'npm run build' 构建 Vue 应用")
                return
            
            url = str(vue_dist / "index.html")
            print(f"生产模式：加载 {url}")
        
        # 创建窗口
        self.window = webview.create_window(
            title='🎯 BakU - 智能备份文件恢复工具',
            url=url,
            width=1200,
            height=800,
            min_size=(800, 600),
            resizable=True,
            maximized=False,
            on_top=False,
            shadow=True,
            debug=dev_mode  # 开发模式下开启调试
        )
        
        # 启动窗口
        print("启动 BakU Vue 界面...")
        webview.start(
            debug=dev_mode,
            func=self.on_window_loaded
        )


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BakU Vue GUI')
    parser.add_argument('--dev', action='store_true', help='开发模式')
    parser.add_argument('--build', action='store_true', help='构建 Vue 应用')
    
    args = parser.parse_args()
    
    if args.build:
        # 构建 Vue 应用
        vue_dir = Path(__file__).parent
        os.chdir(vue_dir)
        
        print("检查依赖...")
        if not (vue_dir / "node_modules").exists():
            print("安装 npm 依赖...")
            os.system("npm install")
        
        print("构建 Vue 应用...")
        result = os.system("npm run build")
        
        if result == 0:
            print("✓ Vue 应用构建成功")
        else:
            print("✗ Vue 应用构建失败")
            return
    
    # 启动应用
    app = BakUVueApp()
    app.run(dev_mode=args.dev)


if __name__ == '__main__':
    main()
