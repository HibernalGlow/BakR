"""
BakR - Streamlit Web界面
现代化的备份文件恢复工具Web版本
"""
import streamlit as st
import streamlit.components.v1
import os
import sys
import math
import tkinter as tk
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Any
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 添加src目录到路径
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from core.backup_finder import BackupFinder
from core.backup_restorer import BackupRestorer


class BakRStreamlitApp:
    """BakR Streamlit应用主类"""
    
    def __init__(self):
        self.backup_finder = BackupFinder()
        self.backup_restorer = BackupRestorer()
        self.init_session_state()
    
    def init_session_state(self):
        """初始化session状态"""
        if 'current_file' not in st.session_state:
            st.session_state.current_file = None
        if 'backup_files' not in st.session_state:
            st.session_state.backup_files = []
        if 'selected_backup' not in st.session_state:
            st.session_state.selected_backup = None
        if 'operation_log' not in st.session_state:
            st.session_state.operation_log = []
        if 'scan_progress' not in st.session_state:
            st.session_state.scan_progress = 0
        if 'last_scan_time' not in st.session_state:
            st.session_state.last_scan_time = None
    
    def log_operation(self, message: str, level: str = "info"):
        """记录操作日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'time': timestamp,
            'level': level,
            'message': message
        }
        st.session_state.operation_log.append(log_entry)
        
        # 限制日志条数
        if len(st.session_state.operation_log) > 100:
            st.session_state.operation_log = st.session_state.operation_log[-100:]
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        import math
        
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def scan_backup_files(self, file_path: Path) -> List[Dict[str, Any]]:
        """扫描备份文件"""
        try:
            self.log_operation(f"开始扫描 {file_path.name} 的备份文件")
            
            # 使用备份查找器
            result = self.backup_finder.find_nearest_backup(str(file_path))
            
            backup_files = []
            if result and result.get('success') and result.get('backup_path'):
                backup_path = Path(result['backup_path'])
                if backup_path.exists():
                    stat = backup_path.stat()
                    backup_files.append({
                        'path': backup_path,
                        'name': backup_path.name,
                        'size': stat.st_size,
                        'size_str': self.format_file_size(stat.st_size),
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'similarity': result.get('similarity', 1.0),
                        'type': backup_path.suffix
                    })
            
            self.log_operation(f"找到 {len(backup_files)} 个备份文件", "success")
            return backup_files
            
        except Exception as ex:
            self.log_operation(f"扫描失败: {str(ex)}", "error")
            return []
    
    def restore_file(self, original_path: Path, backup_path: Path) -> bool:
        """恢复文件"""
        try:
            self.log_operation(f"开始恢复文件: {original_path.name}")
            
            result = self.backup_restorer.restore_backup(original_path, backup_path)
            
            if result.get('success'):
                self.log_operation("文件恢复成功！", "success")
                return True
            else:
                error_msg = result.get('message', '未知错误')
                self.log_operation(f"恢复失败: {error_msg}", "error")
                return False
                
        except Exception as ex:
            self.log_operation(f"恢复过程中发生错误: {str(ex)}", "error")
            return False
    
    def render_header(self):
        """渲染页面头部"""
        st.set_page_config(
            page_title="BakR - 智能备份文件恢复工具",
            page_icon="🔄",
            layout="wide",
            initial_sidebar_state="expanded"
        )
          # 自定义CSS样式和JavaScript
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .main-header h1 {
            color: white;
            margin-bottom: 0.5rem;
        }
        .main-header p {
            color: rgba(255,255,255,0.8);
            margin: 0;
        }
        .file-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 1rem 0;
        }
        .backup-card {
            background: #f1f8e9;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #4caf50;
            margin: 0.5rem 0;
        }
        .log-entry {
            padding: 0.5rem;
            margin: 0.2rem 0;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
        }
        .log-info { background-color: #e3f2fd; }
        .log-success { background-color: #e8f5e8; }
        .log-error { background-color: #ffebee; }
        .log-warning { background-color: #fff3e0; }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .drag-drop-zone {
            border: 2px dashed #cccccc;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            background-color: #f8f9fa;
            margin: 10px 0;
            transition: all 0.3s ease;
        }
        .drag-drop-zone:hover {
            border-color: #667eea;
            background-color: #f0f4ff;
        }
        .drag-drop-zone.drag-over {
            border-color: #4caf50;
            background-color: #e8f5e8;
            transform: scale(1.02);
        }        </style>
        """, unsafe_allow_html=True)
        
        # 主标题
        st.markdown("""
        <div class="main-header">
            <h1>🔄 BakR - 智能备份文件恢复工具</h1>
            <p>Intelligent Backup File Recovery Tool</p>
        </div>
        """, unsafe_allow_html=True)
    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.title("🛠️ 工具面板")
            
            # 文件选择部分
            st.subheader("📁 文件选择")
              # 拖拽区域组件
            st.components.v1.html("""
            <div id="drop-zone" style="
                border: 3px dashed #cccccc;
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                margin: 10px 0;
                cursor: pointer;
                transition: all 0.3s ease;
                min-height: 120px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                position: relative;
            ">
                <div id="drop-content">
                    <div style="font-size: 2.5em; margin-bottom: 10px;">📁</div>
                    <h3 style="margin: 10px 0; color: #495057;">拖拽文件到此处</h3>
                    <p style="color: #6c757d; margin: 5px 0; font-size: 0.9em;">
                        支持从文件资源管理器直接拖拽
                    </p>
                    <p style="color: #6c757d; font-size: 0.8em; margin: 5px 0;">
                        所有文件类型 • 无大小限制 • 获取完整路径
                    </p>
                </div>
                <div id="drop-feedback" style="display: none;">
                    <div style="font-size: 2.5em; margin-bottom: 10px;">✅</div>
                    <h3 style="margin: 10px 0; color: #28a745;">文件已识别</h3>
                    <p id="file-name" style="color: #495057; font-weight: bold;"></p>
                </div>
            </div>

            <script>
                const dropZone = document.getElementById('drop-zone');
                const dropContent = document.getElementById('drop-content');
                const dropFeedback = document.getElementById('drop-feedback');
                const fileName = document.getElementById('file-name');
                
                // 防止默认拖拽行为
                ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                    dropZone.addEventListener(eventName, preventDefaults, false);
                    document.body.addEventListener(eventName, preventDefaults, false);
                });
                
                function preventDefaults(e) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                
                // 拖拽进入
                ['dragenter', 'dragover'].forEach(eventName => {
                    dropZone.addEventListener(eventName, highlight, false);
                });
                
                function highlight(e) {
                    dropZone.style.borderColor = '#007bff';
                    dropZone.style.backgroundColor = '#e3f2fd';
                    dropZone.style.transform = 'scale(1.02)';
                    dropZone.style.boxShadow = '0 8px 25px rgba(0,123,255,0.15)';
                }
                
                // 拖拽离开
                ['dragleave', 'drop'].forEach(eventName => {
                    dropZone.addEventListener(eventName, unhighlight, false);
                });
                
                function unhighlight(e) {
                    dropZone.style.borderColor = '#cccccc';
                    dropZone.style.backgroundColor = 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)';
                    dropZone.style.transform = 'scale(1)';
                    dropZone.style.boxShadow = 'none';
                }
                
                // 处理文件拖拽
                dropZone.addEventListener('drop', handleDrop, false);
                
                function handleDrop(e) {
                    const dt = e.dataTransfer;
                    const files = dt.files;
                    
                    if (files.length > 0) {
                        const file = files[0];
                        // 显示反馈
                        dropContent.style.display = 'none';
                        dropFeedback.style.display = 'block';
                        fileName.textContent = file.name;
                        
                        // 发送文件路径到Streamlit
                        // 由于安全限制，我们发送文件名，让用户确认路径
                        window.parent.postMessage({
                            type: 'streamlit:file-dropped',
                            fileName: file.name,
                            fileSize: file.size,
                            fileType: file.type
                        }, '*');
                        
                        // 3秒后恢复原状
                        setTimeout(() => {
                            dropContent.style.display = 'block';
                            dropFeedback.style.display = 'none';
                        }, 3000);
                    }
                }
                
                // 点击选择文件（备用方案）
                dropZone.addEventListener('click', function() {
                    // 创建隐藏的文件输入
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.style.display = 'none';
                    
                    input.addEventListener('change', function(e) {
                        if (e.target.files.length > 0) {
                            const file = e.target.files[0];
                            dropContent.style.display = 'none';
                            dropFeedback.style.display = 'block';
                            fileName.textContent = file.name;
                            
                            window.parent.postMessage({
                                type: 'streamlit:file-selected',
                                fileName: file.name,
                                fileSize: file.size,
                                fileType: file.type
                            }, '*');
                            
                            setTimeout(() => {
                                dropContent.style.display = 'block';
                                dropFeedback.style.display = 'none';
                            }, 3000);
                        }
                    });
                    
                    input.click();
                });
            </script>
            """, height=200)
            
            # 手动输入文件路径的选项
            st.markdown("**或手动输入文件路径：**")
            file_path_input = st.text_input(
                "文件路径",
                placeholder="请输入完整的文件路径...",
                help="拖拽文件后，请在此确认或修正文件路径",
                key="file_path_input"
            )
              # 提示信息
            st.info("""
            💡 **使用方法：**
            1. 🖱️ 直接拖拽文件到上方蓝色区域
            2. 📝 或手动输入完整文件路径  
            3. 🔍 点击扫描备份开始查找
            
            **支持格式：** 所有文件类型，无大小限制
            """)
            
            # 添加JavaScript来处理拖拽和路径输入的联动
            st.components.v1.html("""
            <script>
                // 监听来自拖拽组件的消息
                window.addEventListener('message', function(event) {
                    if (event.data && event.data.type === 'streamlit:file-dropped') {
                        // 显示文件信息并提示用户输入完整路径
                        const fileName = event.data.fileName;
                        const fileSize = event.data.fileSize;
                        
                        // 尝试找到文件路径输入框并更新提示
                        setTimeout(() => {
                            const inputs = document.querySelectorAll('input[type="text"]');
                            for (let input of inputs) {
                                if (input.placeholder && input.placeholder.includes('文件路径')) {
                                    input.placeholder = `检测到文件: ${fileName} (${(fileSize/1024/1024).toFixed(2)}MB) - 请输入完整路径`;
                                    input.focus();
                                    break;
                                }
                            }
                        }, 100);
                    }
                });
            </script>
            """, height=0)
            
            # 文件路径历史记录
            if 'file_path_history' not in st.session_state:
                st.session_state.file_path_history = []
            
            # 快速路径选择
            if st.session_state.file_path_history:
                st.markdown("**最近使用的文件：**")
                recent_file = st.selectbox(
                    "选择最近的文件",
                    options=[""] + st.session_state.file_path_history[-10:],  # 最近10个
                    index=0,
                    help="快速选择最近处理过的文件"
                )
                
                if recent_file:
                    st.session_state.file_path_input = recent_file
            st.markdown("**快速选择常用目录:**")
            common_dirs = {
                "桌面": str(Path.home() / "Desktop"),
                "文档": str(Path.home() / "Documents"),
                "下载": str(Path.home() / "Downloads"),
                "当前目录": str(Path.cwd())
            }
            
            selected_dir = st.selectbox(
                "常用目录",
                options=list(common_dirs.keys()),
                index=0,
                help="选择常用目录快速导航"
            )
            
            if st.button("📂 浏览目录", use_container_width=True):
                import tkinter as tk
                from tkinter import filedialog
                
                try:
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    
                    selected_file = filedialog.askopenfilename(
                        title="选择要恢复的文件",
                        initialdir=common_dirs[selected_dir],
                        filetypes=[
                            ("所有文件", "*.*"),
                            ("文本文件", "*.txt"),
                            ("文档文件", "*.doc;*.docx;*.pdf"),
                            ("图片文件", "*.jpg;*.png;*.gif;*.bmp"),
                            ("代码文件", "*.py;*.js;*.html;*.css"),
                        ]
                    )
                    
                    if selected_file:
                        st.session_state.file_path_input = selected_file
                        st.rerun()
                        
                except Exception as ex:
                    st.error(f"打开文件对话框失败: {ex}")              # 处理文件路径输入
            if file_path_input and file_path_input.strip():
                file_path = Path(file_path_input.strip())
                if file_path.exists() and file_path.is_file():
                    if st.session_state.current_file != file_path:
                        st.session_state.current_file = file_path
                        
                        # 添加到历史记录
                        file_path_str = str(file_path)
                        if file_path_str not in st.session_state.file_path_history:
                            st.session_state.file_path_history.append(file_path_str)
                            # 限制历史记录数量
                            if len(st.session_state.file_path_history) > 20:
                                st.session_state.file_path_history = st.session_state.file_path_history[-20:]
                        
                        self.log_operation(f"选择文件: {file_path.name}", "success")
                        st.rerun()
                elif file_path_input.strip():
                    st.error(f"❌ 文件不存在或路径无效: {file_path_input}")
                    st.markdown("""
                    **请检查：**
                    - 文件路径是否正确
                    - 文件是否存在
                    - 是否有访问权限
                    """)
            
            # 显示当前选择的文件
            if st.session_state.current_file:
                st.success(f"✅ 已选择: {st.session_state.current_file.name}")
                st.caption(f"📍 路径: {st.session_state.current_file}")
            else:
                st.info("🔽 请拖拽文件到上方区域或输入文件路径")
            
            # 操作按钮
            st.subheader("⚡ 快速操作")
            
            col1, col2 = st.columns(2)
            with col1:
                scan_disabled = not st.session_state.current_file
                if st.button("🔍 扫描备份", 
                           use_container_width=True, 
                           type="primary",
                           disabled=scan_disabled):
                    if st.session_state.current_file:
                        with st.spinner("正在扫描备份文件..."):
                            backup_files = self.scan_backup_files(st.session_state.current_file)
                            st.session_state.backup_files = backup_files
                            st.session_state.last_scan_time = datetime.now()
                        st.rerun()
            
            with col2:
                if st.button("🗑️ 清除", use_container_width=True):
                    st.session_state.current_file = None
                    st.session_state.backup_files = []
                    st.session_state.selected_backup = None
                    st.session_state.file_path_input = ""
                    self.log_operation("已清除所有选择", "info")
                    st.rerun()
            
            # 批量处理部分
            st.subheader("📦 批量处理")
            
            # 批量文件输入
            batch_files_text = st.text_area(
                "批量文件路径",
                placeholder="每行一个文件路径，支持拖拽多个文件...",
                height=100,
                help="将多个文件拖拽到此处，或每行输入一个文件路径"
            )
            
            if batch_files_text:
                batch_files = []
                for line in batch_files_text.strip().split('\n'):
                    line = line.strip()
                    if line and Path(line).exists():
                        batch_files.append(Path(line))
                
                if batch_files:
                    st.info(f"发现 {len(batch_files)} 个有效文件")
                    
                    if st.button("🔍 批量扫描", use_container_width=True, type="secondary"):
                        batch_results = []
                        progress_bar = st.progress(0)
                        
                        for i, file_path in enumerate(batch_files):
                            progress_bar.progress((i + 1) / len(batch_files))
                            backup_files = self.scan_backup_files(file_path)
                            batch_results.append({
                                'file': file_path,
                                'backups': backup_files
                            })
                        
                        st.session_state.batch_results = batch_results
                        self.log_operation(f"批量扫描完成: {len(batch_files)} 个文件", "success")
                        st.rerun()
            
            # 设置部分
            st.subheader("⚙️ 设置")
            
            with st.expander("扫描设置"):
                max_depth = st.slider("最大搜索深度", 1, 10, 5)
                auto_scan = st.checkbox("自动扫描", value=True)
                show_hidden = st.checkbox("显示隐藏文件", value=False)
            
            with st.expander("显示设置"):
                log_level = st.selectbox("日志级别", ["全部", "信息", "成功", "警告", "错误"])
                max_logs = st.number_input("最大日志条数", 10, 1000, 100)
    
    def render_main_content(self):
        """渲染主要内容区域"""
        # 当前文件信息
        if st.session_state.current_file:
            st.subheader("📄 当前文件")
            
            file_path = st.session_state.current_file
            if file_path.exists():
                stat = file_path.stat()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("文件名", file_path.name)
                with col2:
                    st.metric("大小", self.format_file_size(stat.st_size))
                with col3:
                    st.metric("类型", file_path.suffix or "无扩展名")
                with col4:
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    st.metric("修改时间", modified_time.strftime("%m-%d %H:%M"))
                
                # 文件详情卡片
                st.markdown(f"""
                <div class="file-card">
                    <h4>📁 文件详情</h4>
                    <p><strong>完整路径:</strong> {file_path}</p>
                    <p><strong>状态:</strong> <span style="color: green;">✅ 存在</span></p>
                    <p><strong>修改时间:</strong> {modified_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"文件不存在: {file_path}")
        else:
            st.info("👆 请在左侧面板选择文件或上传文件")
        
        # 备份文件列表
        if st.session_state.backup_files:
            st.subheader("💾 发现的备份文件")
            
            # 统计信息
            total_backups = len(st.session_state.backup_files)
            total_size = sum(backup['size'] for backup in st.session_state.backup_files)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("备份文件数量", total_backups)
            with col2:
                st.metric("总大小", self.format_file_size(total_size))
            with col3:
                if st.session_state.last_scan_time:
                    scan_time = st.session_state.last_scan_time.strftime("%H:%M:%S")
                    st.metric("扫描时间", scan_time)
            
            # 备份文件表格
            df_data = []
            for i, backup in enumerate(st.session_state.backup_files):
                df_data.append({
                    '选择': f"备份 {i+1}",
                    '文件名': backup['name'],
                    '大小': backup['size_str'],
                    '修改时间': backup['modified'].strftime('%Y-%m-%d %H:%M:%S'),
                    '相似度': f"{backup['similarity']:.1%}",
                    '类型': backup['type']
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                
                # 使用data_editor来实现选择功能
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "选择": st.column_config.SelectboxColumn(
                            "选择备份",
                            options=[f"备份 {i+1}" for i in range(len(st.session_state.backup_files))],
                            default=None
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # 处理选择
                selected_rows = edited_df[edited_df['选择'].notna()]
                if not selected_rows.empty:
                    selected_idx = int(selected_rows.iloc[0]['选择'].split()[1]) - 1
                    st.session_state.selected_backup = st.session_state.backup_files[selected_idx]
            
            # 显示选中的备份文件详情
            if st.session_state.selected_backup:
                backup = st.session_state.selected_backup
                st.markdown(f"""
                <div class="backup-card">
                    <h4>🎯 选中的备份文件</h4>
                    <p><strong>文件名:</strong> {backup['name']}</p>
                    <p><strong>路径:</strong> {backup['path']}</p>
                    <p><strong>大小:</strong> {backup['size_str']}</p>
                    <p><strong>修改时间:</strong> {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>相似度:</strong> {backup['similarity']:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 恢复操作区域
                st.subheader("🔄 恢复操作")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.warning("⚠️ 恢复操作将覆盖原文件，原文件将备份为 .new")
                
                with col2:
                    if st.button("🔄 确认恢复", type="primary", use_container_width=True):
                        if st.session_state.current_file and st.session_state.selected_backup:
                            with st.spinner("正在恢复文件..."):
                                success = self.restore_file(
                                    st.session_state.current_file,
                                    st.session_state.selected_backup['path']
                                )
                            
                            if success:
                                st.success("✅ 文件恢复成功！")
                                st.balloons()
                            else:
                                st.error("❌ 文件恢复失败！请查看日志获取详细信息。")
        
        elif st.session_state.current_file:
            st.info("🔍 点击'扫描备份'按钮开始查找备份文件")
    
    def render_log_panel(self):
        """渲染日志面板"""
        if st.session_state.operation_log:
            st.subheader("📋 操作日志")
            
            # 日志统计
            log_counts = {}
            for log in st.session_state.operation_log:
                level = log['level']
                log_counts[level] = log_counts.get(level, 0) + 1
            
            if log_counts:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总计", len(st.session_state.operation_log))
                with col2:
                    st.metric("信息", log_counts.get('info', 0))
                with col3:
                    st.metric("成功", log_counts.get('success', 0))
                with col4:
                    st.metric("错误", log_counts.get('error', 0))
            
            # 日志内容
            with st.container():
                # 显示最新的日志（倒序）
                for log in reversed(st.session_state.operation_log[-20:]):
                    level_class = f"log-{log['level']}"
                    icon_map = {
                        'info': 'ℹ️',
                        'success': '✅',
                        'error': '❌',
                        'warning': '⚠️'
                    }
                    icon = icon_map.get(log['level'], 'ℹ️')
                    
                    st.markdown(f"""
                    <div class="log-entry {level_class}">
                        {icon} [{log['time']}] {log['message']}
                    </div>
                    """, unsafe_allow_html=True)
    
    def render_statistics(self):
        """渲染统计信息"""
        if st.session_state.backup_files:
            st.subheader("📊 统计分析")
            
            # 创建图表数据
            chart_data = []
            for backup in st.session_state.backup_files:
                chart_data.append({
                    'name': backup['name'][:20] + '...' if len(backup['name']) > 20 else backup['name'],
                    'size_mb': backup['size'] / (1024 * 1024),
                    'similarity': backup['similarity'] * 100
                })
            
            if chart_data:
                df = pd.DataFrame(chart_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # 文件大小图表
                    fig_size = px.bar(
                        df, 
                        x='name', 
                        y='size_mb',
                        title='备份文件大小 (MB)',
                        labels={'size_mb': '大小 (MB)', 'name': '文件名'}
                    )
                    fig_size.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_size, use_container_width=True)
                
                with col2:
                    # 相似度图表
                    fig_sim = px.bar(
                        df, 
                        x='name', 
                        y='similarity',
                        title='备份文件相似度 (%)',
                        labels={'similarity': '相似度 (%)', 'name': '文件名'},
                        color='similarity',
                        color_continuous_scale='RdYlGn'
                    )
                    fig_sim.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_sim, use_container_width=True)
    
    def run(self):
        """运行应用"""
        self.render_header()
        
        # 创建布局
        self.render_sidebar()
        
        # 主内容区域
        with st.container():
            self.render_main_content()
            
            # 如果有备份文件，显示统计信息
            if st.session_state.backup_files:
                self.render_statistics()
            
            # 日志面板
            self.render_log_panel()
        
        # 页脚
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            <p>🔄 BakR - 智能备份文件恢复工具 | 
            <a href="https://github.com/your-repo/bakr" target="_blank">GitHub</a> | 
            Made with ❤️ and Streamlit</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """主函数"""
    app = BakRStreamlitApp()
    app.run()


if __name__ == "__main__":
    main()
