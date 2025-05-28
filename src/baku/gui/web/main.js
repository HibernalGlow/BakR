const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('file-list');
const progress = document.getElementById('progress');
const resultList = document.getElementById('result-list');
const logDiv = document.getElementById('log');

let queue = [];
let processing = false;

// 主题切换
function toggleTheme() {
    const dark = document.body.classList.toggle('dark');
    localStorage.setItem('baku-theme', dark ? 'dark' : 'light');
}
// 初始化主题
(function() {
    if (localStorage.getItem('baku-theme') === 'dark') document.body.classList.add('dark');
    // 添加主题切换按钮
    const btn = document.createElement('button');
    btn.textContent = '切换主题';
    btn.style = 'position:absolute;top:18px;right:32px;padding:6px 16px;border-radius:6px;background:#4a90e2;color:#fff;border:none;cursor:pointer;font-size:14px;';
    btn.onclick = toggleTheme;
    document.body.appendChild(btn);
})();

// 拖拽交互
function handleFiles(files) {
    for (const f of files) {
        if (!queue.some(q => q.name === f.name && q.size === f.size)) {
            queue.push(f);
        }
    }
    renderQueue();
}
dropZone.addEventListener('dragover', e => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});
dropZone.addEventListener('dragleave', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
});
dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    handleFiles(Array.from(e.dataTransfer.files));
});
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', e => {
    handleFiles(Array.from(fileInput.files));
});

// 渲染队列
function renderQueue() {
    fileList.innerHTML = '';
    queue.forEach((f, idx) => {
        const li = document.createElement('li');
        li.textContent = f.name + ` (${(f.size/1024).toFixed(1)} KB)`;
        li.title = f.name;
        // 删除按钮
        const del = document.createElement('button');
        del.textContent = '移除';
        del.style = 'float:right;background:#f44336;color:#fff;border:none;border-radius:4px;padding:2px 8px;cursor:pointer;font-size:12px;';
        del.onclick = () => { queue.splice(idx,1); renderQueue(); };
        li.appendChild(del);
        fileList.appendChild(li);
    });
}

// 进度条
function showProgress(show) {
    progress.style.display = show ? 'block' : 'none';
}

// 日志
function appendLog(msg, level='info') {
    let color = '#0f0', icon = '';
    if (level==='success') { color='#4caf50'; icon='✔ '; }
    else if (level==='error') { color='#f44336'; icon='✗ '; }
    else if (level==='warn') { color='#ff9800'; icon='⚠ '; }
    else if (level==='info') { color='#2196f3'; icon='ℹ️ '; }
    const line = document.createElement('div');
    line.style.color = color;
    line.style.fontFamily = 'monospace';
    line.textContent = icon + msg;
    logDiv.appendChild(line);
    logDiv.scrollTop = logDiv.scrollHeight;
}

// 批量操作按钮
(function(){
    const bar = document.createElement('div');
    bar.style = 'margin:18px 0 8px 0;text-align:center;';
    // 恢复按钮
    const restoreBtn = document.createElement('button');
    restoreBtn.textContent = '批量恢复';
    restoreBtn.style = 'margin-right:16px;padding:6px 18px;background:#388e3c;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:15px;';
    restoreBtn.onclick = batchRestore;
    // 清空按钮
    const clearBtn = document.createElement('button');
    clearBtn.textContent = '清空队列';
    clearBtn.style = 'padding:6px 18px;background:#d32f2f;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:15px;';
    clearBtn.onclick = () => { queue = []; renderQueue(); appendLog('已清空队列', 'info'); };
    bar.appendChild(restoreBtn);
    bar.appendChild(clearBtn);
    document.querySelector('.container').insertBefore(bar, document.getElementById('progress'));
})();

// 批量恢复模拟
function batchRestore() {
    if (processing || queue.length === 0) return;
    showProgress(true);
    resultList.innerHTML = '';
    appendLog('开始批量恢复...', 'info');
    processing = true;
    let idx = 0;
    function next() {
        if (idx >= queue.length) {
            showProgress(false);
            appendLog('全部恢复完成', 'success');
            processing = false;
            return;
        }
        const f = queue[idx];
        // 模拟处理
        setTimeout(() => {
            const li = document.createElement('li');
            if (Math.random() > 0.1) { // 90%成功
                li.textContent = f.name + ' 恢复成功';
                li.className = 'success';
                appendLog(f.name + ' 恢复成功', 'success');
            } else {
                li.textContent = f.name + ' 恢复失败';
                li.className = 'error';
                appendLog(f.name + ' 恢复失败', 'error');
            }
            resultList.appendChild(li);
            idx++;
            next();
        }, 500);
    }
    next();
}

// 暗色模式样式
(function(){
    const style = document.createElement('style');
    style.textContent = `
    body.dark { background: #181c24; }
    body.dark .container { background: #232a36; box-shadow: 0 2px 12px #0006; }
    body.dark h2 { color: #e3eaf7; }
    body.dark .drop-zone { background: #232a36; color: #90caf9; border-color: #1976d2; }
    body.dark .drop-zone.dragover { background: #1a2230; }
    body.dark #file-list li, body.dark #result-list li { background: #232a36; color: #e3eaf7; }
    body.dark #log { background: #181c24; color: #b9f6ca; }
    `;
    document.head.appendChild(style);
})();

// 初始化日志
appendLog('欢迎使用 BakU 纯前端文件处理工具', 'info'); 