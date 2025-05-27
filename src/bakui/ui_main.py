import webview
import os
from baku.core.multi_file_manager import MultiFileManager
import threading
import json

def on_drop(event):
    print("[BakU] Drop event triggered!")
    files = event['dataTransfer']['files']
    dropped_files = []
    for file in files:
        # pywebviewFullPath 5.0+，否则跳过
        if 'pywebviewFullPath' in file:
            dropped_files.append({
                'name': file['name'],
                'size': file['size'],
                'file_path': file['pywebviewFullPath'],
                'last_modified': file.get('lastModified', None)
            })
    if not dropped_files:
        print("未获取到完整路径，需pywebview 5.0+")
        return
    # 启动线程处理，避免阻塞UI
    threading.Thread(target=process_files, args=(dropped_files,)).start()

def process_files(dropped_files):
    manager = MultiFileManager()
    # 添加文件到队列
    for f in dropped_files:
        manager.add_file_from_info(f['name'], f['size'], f['file_path'], f['last_modified'])
    # 扫描备份
    manager.batch_scan_backups()
    # 恢复文件
    manager.batch_restore_files()
    # 获取结果
    summary = manager.get_queue_summary()
    items = [
        {
            'name': item.name,
            'status': item.status.value,
            'msg': item.message,
            'path': str(item.path) if item.path else '',
            'backup': str(item.selected_backup) if item.selected_backup else ''
        }
        for item in manager.get_all_items()
    ]
    # 回传结果到前端
    js = f"window.showResult({json.dumps({'summary': summary, 'items': items}, ensure_ascii=False)})"
    webview.windows[0].evaluate_js(js)

def setup_drag_drop(window):
    window.events.loaded.wait()
    window.dom.document.events.drop += on_drop
    print("[BakU] 拖拽监听器已设置")

class Api:
    def __init__(self):
        self.manager = MultiFileManager()

    def handle_drop(self, paths: list):
        # paths 是前端传来的本地绝对路径列表
        for path in paths:
            self.manager.add_file_from_info(
                name=path.split('\\')[-1],
                size=0,  # 可选：os.path.getsize(path)
                file_path=path
            )
        # 这里可以自动扫描和恢复
        self.manager.batch_scan_backups()
        self.manager.batch_restore_files()
        # 返回处理结果
        items = []
        for item in self.manager.get_all_items():
            items.append({
                'name': item.name,
                'backup': str(item.selected_backup) if item.selected_backup else '',
                'status': item.status.value,
                'msg': item.message,
                'path': str(item.path) if item.path else ''
            })
        return items

def start_ui():
    api = Api()
    html_path = 'file://' + os.path.abspath('src/bakui/web/vue/dist/index.html')
    webview.create_window('BakU 智能备份恢复工具', html_path, js_api=api, width=1100, height=700)
    webview.start(debug=True, gui='edgechromium')

if __name__ == '__main__':
    start_ui() 