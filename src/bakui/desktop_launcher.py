import webview
import subprocess
import time
import os

# 启动 FastAPI 后端
api_proc = subprocess.Popen([
    'uvicorn', 'bakui.api:app', '--host', '127.0.0.1', '--port', '8000'
])
time.sleep(2)  # 等待API启动

# 启动前端（假设已build，静态文件在 web/vue/dist）
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web', 'vue', 'dist', 'index.html'))
webview.create_window('BakU 智能备份恢复工具', f'file://{frontend_path}', width=1100, height=700)
webview.start()

api_proc.terminate()
