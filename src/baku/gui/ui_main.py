import webview
import os
import baku
import json
from baku.core.backup_finder import BackupFinder
from baku.core.backup_restorer import BackupRestorer
from baku.core.multi_file_manager import MultiFileManager
from baku.core.file_queue import FileQueueItem, FileStatus
import time
from pathlib import Path
from loguru import logger

class Api:
    def process_files(self, files, auto_mode=True):
        file_paths = [file.get('pywebviewFullPath') for file in files if file.get('pywebviewFullPath')]
        backup_finder = BackupFinder()
        backup_restorer = BackupRestorer()
        file_manager = MultiFileManager(backup_finder, backup_restorer)
        bak_trace = []
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
        # 自动模式：优先用同目录bak，否则回溯
        results = []
        for item in file_manager.file_queue.items:
            bak_path = None
            # 1. 优先同目录bak
            bak_candidate = item.path.with_suffix(item.path.suffix + '.bak')
            if auto_mode and bak_candidate.exists():
                bak_path = str(bak_candidate)
                try:
                    backup_restorer.restore_backup(bak_candidate, item.path)
                    status = 'success'
                    msg = f'优先用同目录bak恢复: {bak_path}'
                except Exception as e:
                    status = 'error'
                    msg = f'bak恢复失败: {e}'
            else:
                # 2. 回溯查找
                found = backup_finder.find_nearest_backup(item.path)
                if found:
                    bak_path = str(found)
                    try:
                        backup_restorer.restore_backup(found, item.path)
                        status = 'success'
                        msg = f'回溯bak恢复: {bak_path}'
                    except Exception as e:
                        status = 'error'
                        msg = f'回溯bak恢复失败: {e}'
                else:
                    status = 'error'
                    msg = '未找到bak文件'
            bak_trace.append({'file': str(item.path), 'bak': bak_path})
            results.append({
                'file': str(item.path),
                'bak_used': bak_path,
                'status': status,
                'message': msg
            })
        # 记录追踪日志
        logger.info(f"拖入文件与bak追踪: {json.dumps(bak_trace, ensure_ascii=False)}")
        return results

def on_drop(event, window):
    files = event['dataTransfer']['files']
    file_list = [f for f in files if 'pywebviewFullPath' in f]
    # 兼容前端传递auto_mode
    auto_mode = True
    if hasattr(window, 'auto_mode'):
        auto_mode = window.auto_mode
    paths_json = json.dumps([f['pywebviewFullPath'] for f in file_list])
    window.evaluate_js(f'window.showProcessing({paths_json})')
    api = Api()
    process_results = api.process_files(file_list, auto_mode=auto_mode)
    results_json = json.dumps(process_results)
    window.evaluate_js(f'window.showResults({results_json})')

def setup_drag_drop(window):
    window.events.loaded.wait()
    window.dom.document.events.drop += lambda event: on_drop(event, window)

def start_ui():
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'vue', 'dist', 'index.html'))
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