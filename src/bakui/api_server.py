from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from baku.core.multi_file_manager import MultiFileManager
from pathlib import Path
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请指定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = MultiFileManager()

class FileInfo(BaseModel):
    name: str
    size: int
    path: str
    lastModified: Optional[int] = None

@app.post("/api/add_files")
async def add_files(files: List[FileInfo], auto_mode: bool = False):
    # 清空队列，重新添加
    manager.clear_queue()
    for f in files:
        manager.add_file_from_info(f.name, f.size, f.path, f.lastModified)
    # 自动模式：bak文件直接恢复，普通文件自动查找bak并恢复
    if auto_mode:
        # 先扫描备份
        manager.batch_scan_backups()
        # 自动恢复所有可恢复文件
        manager.batch_restore_files()
    return get_status()

@app.post("/api/restore_file")
async def restore_file(file_id: str):
    # 恢复指定文件
    manager.restore_file(file_id)
    return get_status()

@app.get("/api/status")
def get_status():
    items = []
    for item in manager.get_all_items():
        items.append({
            "id": item.id,
            "name": item.name,
            "path": str(item.path) if item.path else '',
            "backup_name": item.selected_backup.name if item.selected_backup else '',
            "backup_path": str(item.selected_backup) if item.selected_backup else '',
            "status": item.status.value,
            "status_text": item.message,
        })
    progress = f"队列共 {len(items)} 个文件。"
    return {"items": items, "progress": progress}

@app.post("/api/clear")
def clear_queue():
    manager.clear_queue()
    return get_status()

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True) 