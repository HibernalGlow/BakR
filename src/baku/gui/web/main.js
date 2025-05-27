const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('file-list');
const progress = document.getElementById('progress');
const resultList = document.getElementById('result-list');
const logDiv = document.getElementById('log');

// 拖拽交互
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
    fileList.innerHTML = '';
    resultList.innerHTML = '';
    const files = Array.from(e.dataTransfer.files);
    files.forEach(f => {
        const li = document.createElement('li');
        li.textContent = f.name;
        fileList.appendChild(li);
    });
    // 让pywebview处理拖拽事件
});
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', e => {
    fileList.innerHTML = '';
    resultList.innerHTML = '';
    const files = Array.from(fileInput.files);
    files.forEach(f => {
        const li = document.createElement('li');
        li.textContent = f.name;
        fileList.appendChild(li);
    });
    // 让pywebview处理文件选择事件（可扩展）
});

// pywebview回调：显示处理中动画
window.showProcessing = function(paths) {
    fileList.innerHTML = '';
    resultList.innerHTML = '';
    (paths || []).forEach(path => {
        const li = document.createElement('li');
        li.textContent = path;
        fileList.appendChild(li);
    });
    progress.style.display = 'block';
}
// pywebview回调：显示处理结果
window.showResults = function(results) {
    progress.style.display = 'none';
    resultList.innerHTML = '';
    (results || []).forEach(item => {
        const li = document.createElement('li');
        li.textContent = `${item.file}：${item.result && item.result.status ? item.result.status : item.result}`;
        li.className = item.result && item.result.status === 'success' ? 'success' : (item.result && item.result.status === 'error' ? 'error' : '');
        resultList.appendChild(li);
    });
}
// 日志追加方法，带高亮
window.appendLog = function(msg) {
    let color = '#0f0'; // 默认绿色
    let icon = '';
    if (/SUCCESS|✔|✓/.test(msg)) { color = '#4caf50'; icon = '✔ '; }
    else if (/ERROR|✗|❌|失败/.test(msg)) { color = '#f44336'; icon = '✗ '; }
    else if (/WARN|警告/.test(msg)) { color = '#ff9800'; icon = '⚠ '; }
    else if (/INFO|ℹ️/.test(msg)) { color = '#2196f3'; icon = 'ℹ️ '; }
    const line = document.createElement('div');
    line.style.color = color;
    line.style.fontFamily = 'monospace';
    line.textContent = icon + msg;
    logDiv.appendChild(line);
    logDiv.scrollTop = logDiv.scrollHeight;
} 