from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from baku.core.multi_file_manager import MultiFileManager
import shutil, os, tempfile

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

manager = MultiFileManager()
auto_mode = True

@app.post('/api/upload')
async def upload(files: list[UploadFile] = File(...)):
    results = []
    for f in files:
        tmp_path = os.path.join(tempfile.gettempdir(), f.filename)
        with open(tmp_path, 'wb') as out:
            shutil.copyfileobj(f.file, out)
        manager.add_file_from_info(f.filename, os.path.getsize(tmp_path), tmp_path)
        results.append({'name': f.filename, 'path': tmp_path})
    if auto_mode:
        manager.batch_scan_backups()
        manager.batch_restore_files()
    return {"success": True, "results": results, "queue": get_queue()}

@app.post('/api/restore')
async def restore(request: Request):
    data = await request.json()
    file_ids = data.get('file_ids', [])
    manager.batch_restore_files(file_ids)
    return {"success": True, "queue": get_queue()}

@app.post('/api/clear')
async def clear():
    manager.clear_queue()
    return {"success": True, "queue": get_queue()}

@app.post('/api/auto_mode')
async def set_auto_mode(request: Request):
    global auto_mode
    data = await request.json()
    auto_mode = data.get('on', True)
    return {"auto_mode": auto_mode}

@app.get('/api/status')
async def status():
    return {"queue": get_queue()}

def get_queue():
    items = []
    for item in manager.get_all_items():
        items.append({
            'id': item.id,
            'name': item.name,
            'backup': str(item.selected_backup) if item.selected_backup else '',
            'status': item.status.value,
            'msg': item.message,
            'path': str(item.path) if item.path else ''
        })
    return items
