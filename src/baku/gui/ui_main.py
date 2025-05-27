import webview
import os
import baku  # 假设baku包已正确安装/可import
import json
from baku.core.backup_finder import BackupFinder
from baku.core.backup_restorer import BackupRestorer
from baku.core.multi_file_manager import MultiFileManager
from baku.core.file_queue import FileQueueItem, FileStatus
import time
from pathlib import Path
from loguru import logger

class Api:
    def process_files(self, files):
        file_paths = [file.get('pywebviewFullPath') for file in files if file.get('pywebviewFullPath')]
        backup_finder = BackupFinder()
        backup_restorer = BackupRestorer()
        file_manager = MultiFileManager(backup_finder, backup_restorer)
        # 添加文件到队列
        for path in file_paths:
            p = Path(path)
            file_item = FileQueueItem(
                id=f"{p.name}_{p.stat().st_size}_{int(time.time())}",
                name=p.name,
                path=p,
                size=p.stat().st_size,
                status=FileStatus.PENDING,
                message="已添加到队列"
            )
            file_manager.file_queue.add_item(file_item)
        # 自动扫描和恢复
        file_manager.batch_scan_backups()
        file_manager.batch_restore_files()
        # 收集结果
        results = []
        for item in file_manager.file_queue.items:
            results.append({
                'file': str(item.path),
                'status': item.status.value,
                'message': item.message
            })
        return results

def on_drop(event, window):
    files = event['dataTransfer']['files']
    file_list = [f for f in files if 'pywebviewFullPath' in f]
    paths_json = json.dumps([f['pywebviewFullPath'] for f in file_list])
    window.evaluate_js(f'window.showProcessing({paths_json})')
    api = Api()
    process_results = api.process_files(file_list)
    results_json = json.dumps(process_results)
    window.evaluate_js(f'window.showResults({results_json})')

def setup_drag_drop(window):
    window.events.loaded.wait()
    # 用lambda或partial传递window
    window.dom.document.events.drop += lambda event: on_drop(event, window)

def start_ui():
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web', 'index.html'))
    window = webview.create_window('BakU 拖拽文件', f'file://{html_path}', width=700, height=500)

    # 注册 loguru sink，将日志推送到前端
    def gui_log_sink(msg):
        safe_msg = str(msg).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        try:
            window.evaluate_js(f"window.appendLog('{safe_msg}')")
        except Exception:
            pass  # 窗口未就绪时忽略
    logger.add(gui_log_sink, level="INFO")

    webview.start(setup_drag_drop, window, debug=False, gui='edgechromium')

if __name__ == '__main__':
    start_ui() 