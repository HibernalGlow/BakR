// BakR JavaScript 功能
class BakRApp {
    constructor() {
        this.currentFile = null;
        this.currentBackup = null;
        this.tauriAvailable = false;
        this.initializeElements();
        this.bindEvents();
        this.checkTauriAvailability();
        this.addLog('info', '应用启动成功');
    }

    async checkTauriAvailability() {
        // 检查是否在 Tauri 环境中运行
        try {
            if (window.__TAURI__ || window.tauri) {
                this.tauriAvailable = true;
                this.addLog('success', '✅ Tauri 环境检测成功');
                
                // 监听 Tauri 事件
                this.setupTauriEventListeners();
                
                // 获取应用信息
                const appInfo = await this.invokeCommand('get_app_info');
                if (appInfo) {
                    this.addLog('info', `应用信息: ${appInfo.name} v${appInfo.version}`);
                }
            } else {
                this.addLog('warning', '⚠️ 非 Tauri 环境，使用演示模式');
                this.setupDemoMode();
            }
        } catch (error) {
            this.addLog('error', `环境检测失败: ${error.message}`);
            this.setupDemoMode();
        }
    }

    async setupTauriEventListeners() {
        try {
            const { listen } = window.__TAURI__.event;
            
            // 监听日志事件
            await listen('log', (event) => {
                const { type, message } = event.payload;
                this.addLog(type, message);
            });
            
            // 监听应用就绪事件
            await listen('app_ready', (event) => {
                this.addLog('success', '🚀 后端应用初始化完成');
            });
            
            // 监听恢复完成事件
            await listen('restore_complete', (event) => {
                const result = event.payload;
                this.addLog('success', `✅ 恢复完成: ${result.message}`);
                this.showRestoreSuccess(result);
            });
            
        } catch (error) {
            this.addLog('error', `事件监听设置失败: ${error.message}`);
        }
    }

    setupDemoMode() {
        // 演示模式的模拟功能
        this.addLog('info', '📱 演示模式：您可以体验界面功能');
        this.addLog('info', '💡 要获得完整功能，请安装 PyTauri 并运行桌面应用');
    }

    async invokeCommand(command, args = {}) {
        if (!this.tauriAvailable) {
            // 演示模式的模拟响应
            return this.mockCommand(command, args);
        }
        
        try {
            const { invoke } = window.__TAURI__.tauri;
            return await invoke(command, args);
        } catch (error) {
            this.addLog('error', `命令调用失败 (${command}): ${error.message}`);
            throw error;
        }
    }

    mockCommand(command, args) {
        // 演示模式的模拟命令响应
        this.addLog('info', `模拟命令: ${command}`);
        
        switch (command) {
            case 'get_app_info':
                return Promise.resolve({
                    name: 'BakR',
                    version: '0.1.0',
                    description: '智能备份文件恢复工具',
                    supported_extensions: ['.bak', '.backup', '.old'],
                    tauri_available: false
                });
                
            case 'find_backup':
                return Promise.resolve({
                    success: true,
                    message: '演示：模拟找到备份文件',
                    data: {
                        backup_found: true,
                        backup_file: args.file_path + '.bak',
                        search_info: {
                            target_file: args.file_path,
                            search_paths: [
                                { path: args.file_path + '.bak', level: '同级目录', exists: true }
                            ]
                        },
                        preview: {
                            target_file: { path: args.file_path, exists: true, size: 1024 },
                            backup_file: { path: args.file_path + '.bak', exists: true, size: 2048 },
                            new_file: { path: args.file_path + '.new', will_create: true },
                            can_restore: true
                        }
                    }
                });
                
            default:
                return Promise.resolve({ success: false, message: '演示模式：命令不可用' });
        }
    }

    initializeElements() {
        // DOM 元素引用
        this.dropZone = document.getElementById('dropZone');
        this.browseBtn = document.getElementById('browseBtn');
        this.fileInfo = document.getElementById('fileInfo');
        this.targetFileDetails = document.getElementById('targetFileDetails');
        this.backupCard = document.getElementById('backupCard');
        this.backupFileDetails = document.getElementById('backupFileDetails');
        this.noBackupCard = document.getElementById('noBackupCard');
        this.searchResults = document.getElementById('searchResults');
        this.previewBtn = document.getElementById('previewBtn');
        this.restoreBtn = document.getElementById('restoreBtn');
        this.previewModal = document.getElementById('previewModal');
        this.previewContent = document.getElementById('previewContent');
        this.closePreview = document.getElementById('closePreview');
        this.cancelRestore = document.getElementById('cancelRestore');
        this.confirmRestore = document.getElementById('confirmRestore');
        this.logContent = document.getElementById('logContent');
        this.clearLogBtn = document.getElementById('clearLogBtn');
        this.loading = document.getElementById('loading');
    }

    bindEvents() {
        // 拖拽事件
        this.dropZone.addEventListener('dragover', this.handleDragOver.bind(this));
        this.dropZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.dropZone.addEventListener('drop', this.handleDrop.bind(this));
        
        // 点击浏览按钮
        this.browseBtn.addEventListener('click', this.handleBrowseClick.bind(this));
        
        // 按钮事件
        this.previewBtn.addEventListener('click', this.handlePreview.bind(this));
        this.restoreBtn.addEventListener('click', this.handleRestore.bind(this));
        this.closePreview.addEventListener('click', this.closePreviewModal.bind(this));
        this.cancelRestore.addEventListener('click', this.closePreviewModal.bind(this));
        this.confirmRestore.addEventListener('click', this.handleConfirmRestore.bind(this));
        this.clearLogBtn.addEventListener('click', this.clearLog.bind(this));
        
        // 模态框点击外部关闭
        this.previewModal.addEventListener('click', (e) => {
            if (e.target === this.previewModal) {
                this.closePreviewModal();
            }
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        this.dropZone.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.dropZone.classList.remove('dragover');
    }    async handleDrop(e) {
        e.preventDefault();
        this.dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            await this.processFile(file.path || file.name);
        }
    }

    async handleBrowseClick() {
        try {
            if (this.tauriAvailable) {
                // 在 Tauri 环境中使用文件对话框
                const { open } = window.__TAURI__.dialog;
                const selected = await open({
                    multiple: false,
                    filters: [{
                        name: 'All Files',
                        extensions: ['*']
                    }]
                });
                
                if (selected) {
                    await this.processFile(selected);
                }
            } else {
                // 演示模式
                this.addLog('info', '演示模式：模拟文件选择');
                this.simulateFileSelection();
            }
        } catch (error) {
            this.addLog('error', `文件选择失败: ${error.message}`);
        }
    }

    simulateFileSelection() {
        // 模拟选择文件进行演示
        const demoFile = 'C:\\Users\\Demo\\Documents\\important.txt';
        this.processFile(demoFile);
    }

    async processFile(filePath) {
        try {
            this.showLoading(true);
            this.addLog('info', `处理文件: ${filePath}`);
            
            // 调用后端查找备份文件
            const result = await this.invokeCommand('find_backup', { file_path: filePath });
            
            this.currentFile = filePath;
            this.displayFileInfo(result);
            
        } catch (error) {
            this.addLog('error', `处理文件失败: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    // 模拟后端调用（在真实环境中会调用 PyTauri 的 invoke）
    async mockFindBackup(filePath) {
        // 模拟网络延迟
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 模拟查找结果
        const hasBackup = Math.random() > 0.3; // 70% 概率找到备份
        
        if (hasBackup) {
            return {
                success: true,
                message: `找到备份文件: ${filePath}.bak`,
                data: {
                    backup_found: true,
                    backup_file: `${filePath}.bak`,
                    search_info: {
                        target_file: filePath,
                        search_paths: [
                            { path: `${filePath}.bak`, level: '同级目录', exists: true },
                            { path: `${filePath}.backup`, level: '同级目录', exists: false },
                            { path: `${filePath}.old`, level: '同级目录', exists: false }
                        ]
                    },
                    preview: {
                        target_file: {
                            path: filePath,
                            exists: true,
                            size: 1024,
                            modified: new Date().toISOString()
                        },
                        backup_file: {
                            path: `${filePath}.bak`,
                            exists: true,
                            size: 1200,
                            modified: new Date(Date.now() - 86400000).toISOString()
                        },
                        new_file: {
                            path: `${filePath}.new`,
                            will_create: true
                        },
                        can_restore: true
                    }
                }
            };
        } else {
            return {
                success: true,
                message: '未找到对应的备份文件',
                data: {
                    backup_found: false,
                    backup_file: null,
                    search_info: {
                        target_file: filePath,
                        search_paths: [
                            { path: `${filePath}.bak`, level: '同级目录', exists: false },
                            { path: `${filePath}.backup`, level: '同级目录', exists: false },
                            { path: `${filePath}.old`, level: '同级目录', exists: false }
                        ]
                    },
                    preview: null
                }
            };
        }
    }

    displayFileInfo(result) {
        this.fileInfo.style.display = 'block';
        
        // 显示目标文件信息
        this.targetFileDetails.innerHTML = `
            <strong>文件路径:</strong> ${result.data.search_info.target_file}<br>
            <strong>状态:</strong> <span style="color: green;">存在</span>
        `;
        
        if (result.data.backup_found) {
            // 找到备份文件
            this.currentBackup = result.data.backup_file;
            this.backupCard.style.display = 'block';
            this.noBackupCard.style.display = 'none';
            
            this.backupFileDetails.innerHTML = `
                <strong>备份文件:</strong> ${result.data.backup_file}<br>
                <strong>状态:</strong> <span style="color: green;">找到</span>
            `;
            
            this.addLog('success', `找到备份文件: ${result.data.backup_file}`);
        } else {
            // 未找到备份文件
            this.backupCard.style.display = 'none';
            this.noBackupCard.style.display = 'block';
            
            this.displaySearchResults(result.data.search_info.search_paths);
            this.addLog('warning', '未找到对应的备份文件');
        }
    }

    displaySearchResults(searchPaths) {
        this.searchResults.innerHTML = searchPaths.map(item => `
            <div class="search-item">
                <span class="search-path">${item.path}</span>
                <span class="search-status ${item.exists ? 'found' : 'not-found'}">
                    ${item.exists ? '存在' : '不存在'}
                </span>
            </div>
        `).join('');
    }

    async handlePreview() {
        if (!this.currentBackup) return;
        
        try {
            this.showLoading(true);
            // 在真实环境中调用预览 API
            const preview = await this.mockPreviewRestore();
            this.showPreviewModal(preview);
        } catch (error) {
            this.addLog('error', `预览失败: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    async mockPreviewRestore() {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            target_file: {
                path: this.currentFile,
                exists: true,
                size: 1024,
                modified: new Date().toISOString()
            },
            backup_file: {
                path: this.currentBackup,
                exists: true,
                size: 1200,
                modified: new Date(Date.now() - 86400000).toISOString()
            },
            new_file: {
                path: `${this.currentFile}.new`,
                will_create: true
            },
            can_restore: true
        };
    }

    showPreviewModal(preview) {
        const formatDate = (isoString) => {
            return new Date(isoString).toLocaleString('zh-CN');
        };
        
        const formatSize = (bytes) => {
            return bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KB`;
        };
        
        this.previewContent.innerHTML = `
            <div class="preview-section">
                <h4>📄 目标文件</h4>
                <div class="file-preview">
                    <p><strong>路径:</strong> ${preview.target_file.path}</p>
                    <p><strong>大小:</strong> ${formatSize(preview.target_file.size)}</p>
                    <p><strong>修改时间:</strong> ${formatDate(preview.target_file.modified)}</p>
                </div>
            </div>
            
            <div class="preview-section">
                <h4>💾 备份文件</h4>
                <div class="file-preview">
                    <p><strong>路径:</strong> ${preview.backup_file.path}</p>
                    <p><strong>大小:</strong> ${formatSize(preview.backup_file.size)}</p>
                    <p><strong>修改时间:</strong> ${formatDate(preview.backup_file.modified)}</p>
                </div>
            </div>
            
            <div class="preview-section">
                <h4>🔄 恢复操作</h4>
                <div class="operation-preview">
                    <p>✅ 将当前文件备份为: <code>${preview.new_file.path}</code></p>
                    <p>✅ 将备份文件恢复到: <code>${preview.target_file.path}</code></p>
                </div>
            </div>
            
            <div class="warning-box">
                <p><strong>⚠️ 注意:</strong> 此操作将替换当前文件内容，原文件将备份为 .new 扩展名。</p>
            </div>
        `;
        
        this.previewModal.style.display = 'flex';
    }

    closePreviewModal() {
        this.previewModal.style.display = 'none';
    }

    async handleRestore() {
        // 直接调用确认恢复
        await this.handleConfirmRestore();
    }

    async handleConfirmRestore() {
        if (!this.currentBackup) return;
        
        try {
            this.showLoading(true);
            this.closePreviewModal();
            
            // 在真实环境中调用恢复 API
            const result = await this.mockRestoreBackup();
            
            if (result.success) {
                this.addLog('success', result.message);
                this.showSuccessMessage('恢复成功！', result.message);
            } else {
                this.addLog('error', result.message);
                this.showErrorMessage('恢复失败', result.message);
            }
            
        } catch (error) {
            this.addLog('error', `恢复失败: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    async mockRestoreBackup() {
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // 模拟 90% 成功率
        const success = Math.random() > 0.1;
        
        if (success) {
            return {
                success: true,
                message: `成功恢复 ${this.currentBackup} 到 ${this.currentFile}`,
                details: {
                    target_file: this.currentFile,
                    backup_file: this.currentBackup,
                    new_file: `${this.currentFile}.new`,
                    timestamp: new Date().toISOString()
                }
            };
        } else {
            return {
                success: false,
                message: '文件被占用，无法执行恢复操作',
                details: { error: 'File in use' }
            };
        }
    }

    // 显示恢复成功结果
    showRestoreSuccess(result) {
        const message = `恢复操作完成！\n\n详细信息:\n- 目标文件: ${result.details.target_file}\n- 备份文件: ${result.details.backup_file}\n- 原文件备份为: ${result.details.new_file || '无需备份'}`;
        this.showSuccessMessage('恢复成功', message);
    }

    showSuccessMessage(title, message) {
        // 在真实环境中可以使用 Tauri 的通知 API
        alert(`${title}\n\n${message}`);
    }

    showErrorMessage(title, message) {
        alert(`${title}\n\n${message}`);
    }

    showLoading(show) {
        this.loading.style.display = show ? 'flex' : 'none';
    }

    addLog(type, message) {
        const timestamp = new Date().toLocaleTimeString('zh-CN');
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="message">${message}</span>
        `;
        
        this.logContent.appendChild(logEntry);
        this.logContent.scrollTop = this.logContent.scrollHeight;
    }

    clearLog() {
        this.logContent.innerHTML = '';
        this.addLog('info', '日志已清空');
    }
}

// 添加预览样式
const style = document.createElement('style');
style.textContent = `
    .preview-section {
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #eee;
    }
    
    .preview-section:last-of-type {
        border-bottom: none;
    }
    
    .preview-section h4 {
        margin-bottom: 10px;
        color: #333;
    }
    
    .file-preview {
        background: #f8f9fa;
        padding: 12px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
    }
    
    .operation-preview {
        background: #e8f5e8;
        padding: 12px;
        border-radius: 4px;
        font-size: 14px;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 12px;
        border-radius: 4px;
        color: #856404;
        font-size: 14px;
    }
    
    code {
        background: #e9ecef;
        padding: 2px 4px;
        border-radius: 2px;
        font-family: 'Courier New', monospace;
    }
`;
document.head.appendChild(style);

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new BakRApp();
});
