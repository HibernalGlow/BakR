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

def start_ui():
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web', 'drag_drop.html'))
    window = webview.create_window('BakU 拖拽文件', f'file://{html_path}', width=700, height=500)
    webview.start(setup_drag_drop, window, debug=True, gui='edgechromium')

if __name__ == '__main__':
    start_ui() 