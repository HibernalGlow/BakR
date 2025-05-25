"""
文件选择组件
提供多种文件选择方式
"""
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import os
from typing import Optional, List


class FileSelector:
    """文件选择器组件"""
    
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        """初始化session状态"""
        if 'file_history' not in st.session_state:
            st.session_state.file_history = []
        if 'common_dirs' not in st.session_state:
            # 常用目录
            st.session_state.common_dirs = [
                str(Path.home() / "Documents"),
                str(Path.home() / "Desktop"),
                str(Path.home() / "Downloads"),
                "C:\\Program Files",
                "C:\\Users",
                str(Path.cwd())
            ]
    
    def render_drag_drop_zone(self, key: str = "drag_drop", height: int = 400) -> Optional[List[dict]]:
        """渲染拖拽区域"""
        # 读取HTML文件内容
        html_file = Path(__file__).parent.parent / "static" / "drag_drop.html"
        if html_file.exists():
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            # 如果文件不存在，使用简化版本
            html_content = self._get_simple_drag_drop_html()
          # 渲染组件
        result = components.html(
            html_content,
            height=height
        )
        
        return result
    
    def _get_simple_drag_drop_html(self) -> str:
        """获取简化的拖拽HTML"""
        return """
        <div id="dropZone" style="
            border: 2px dashed #cccccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background-color: #f8f9fa;
            cursor: pointer;
            transition: all 0.3s ease;
        ">
            <div style="font-size: 48px; margin-bottom: 15px;">📁</div>
            <div style="font-size: 16px; color: #666; margin-bottom: 10px;">拖拽文件到这里</div>
            <div style="font-size: 14px; color: #999;">或点击选择文件</div>
        </div>
        
        <script>
            const dropZone = document.getElementById('dropZone');
            
            dropZone.addEventListener('click', function() {
                const input = document.createElement('input');
                input.type = 'file';
                input.multiple = true;
                input.onchange = function(e) {
                    const files = Array.from(e.target.files).map(file => ({
                        name: file.name,
                        size: file.size,
                        lastModified: file.lastModified,
                        type: file.type
                    }));
                    
                    window.parent.postMessage({
                        type: 'multi_file_drop',
                        files: files
                    }, '*');
                };
                input.click();
            });
            
            // 拖拽事件
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                }, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, function() {
                    dropZone.style.borderColor = '#667eea';
                    dropZone.style.backgroundColor = '#f0f4ff';
                }, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, function() {
                    dropZone.style.borderColor = '#cccccc';
                    dropZone.style.backgroundColor = '#f8f9fa';
                }, false);
            });
            
            dropZone.addEventListener('drop', function(e) {
                const files = Array.from(e.dataTransfer.files).map(file => ({
                    name: file.name,
                    size: file.size,
                    lastModified: file.lastModified,
                    type: file.type
                }));
                
                window.parent.postMessage({
                    type: 'multi_file_drop',
                    files: files
                }, '*');
            }, false);
        </script>
        """
    
    def render_manual_input(self) -> Optional[str]:
        """渲染手动输入文件路径"""
        st.subheader("手动输入文件路径")
        
        # 文件路径输入
        file_path = st.text_input(
            "文件路径",
            placeholder="输入完整的文件路径...",
            help="请输入要恢复的文件的完整路径"
        )
        
        # 路径验证
        if file_path:
            path = Path(file_path)
            if path.exists():
                if path.is_file():
                    st.success(f"✅ 文件存在: {path.name}")
                    stat = path.stat()
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("文件大小", self._format_file_size(stat.st_size))
                    with col2:
                        st.metric("文件类型", path.suffix or "无扩展名")
                    with col3:
                        st.metric("修改时间", path.stat().st_mtime)
                    
                    # 添加到历史记录
                    if st.button("添加到队列", key="add_manual"):
                        self._add_to_history(file_path)
                        return file_path
                else:
                    st.error("❌ 这是一个目录，请输入文件路径")
            else:
                st.error("❌ 文件不存在，请检查路径")
        
        return None
    
    def render_file_browser(self) -> Optional[str]:
        """渲染文件浏览器"""
        st.subheader("浏览文件")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🗂️ 打开文件浏览器", key="open_browser"):
                try:
                    # 创建隐藏的tkinter窗口
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    
                    # 打开文件对话框
                    file_path = filedialog.askopenfilename(
                        title="选择要恢复的文件",
                        filetypes=[
                            ("所有文件", "*.*"),
                            ("文本文件", "*.txt"),
                            ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp"),
                            ("文档文件", "*.doc *.docx *.pdf *.rtf"),
                            ("数据文件", "*.csv *.xlsx *.json *.xml")
                        ]
                    )
                    
                    root.destroy()
                    
                    if file_path:
                        self._add_to_history(file_path)
                        st.success(f"已选择文件: {Path(file_path).name}")
                        return file_path
                        
                except Exception as ex:
                    st.error(f"打开文件浏览器失败: {str(ex)}")
        
        with col2:
            if st.button("🗂️ 选择多个文件", key="open_multi_browser"):
                try:
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    
                    file_paths = filedialog.askopenfilenames(
                        title="选择多个文件",
                        filetypes=[("所有文件", "*.*")]
                    )
                    
                    root.destroy()
                    
                    if file_paths:
                        for path in file_paths:
                            self._add_to_history(path)
                        st.success(f"已选择 {len(file_paths)} 个文件")
                        return list(file_paths)
                        
                except Exception as ex:
                    st.error(f"打开文件浏览器失败: {str(ex)}")
        
        return None
    
    def render_common_directories(self):
        """渲染常用目录"""
        st.subheader("常用目录")
        
        for directory in st.session_state.common_dirs:
            if Path(directory).exists():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(directory)
                with col2:
                    if st.button("📂", key=f"browse_{directory}", help="浏览此目录"):
                        try:
                            # 在此目录打开文件选择器
                            root = tk.Tk()
                            root.withdraw()
                            root.attributes('-topmost', True)
                            
                            file_path = filedialog.askopenfilename(
                                title=f"从 {directory} 选择文件",
                                initialdir=directory,
                                filetypes=[("所有文件", "*.*")]
                            )
                            
                            root.destroy()
                            
                            if file_path:
                                self._add_to_history(file_path)
                                st.success(f"已选择: {Path(file_path).name}")
                                
                        except Exception as ex:
                            st.error(f"浏览目录失败: {str(ex)}")
    
    def render_file_history(self):
        """渲染文件历史记录"""
        if not st.session_state.file_history:
            return
        
        st.subheader("最近使用的文件")
        
        # 清空历史按钮
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗑️ 清空历史", key="clear_history"):
                st.session_state.file_history = []
                st.rerun()
        
        # 显示历史文件
        for i, file_path in enumerate(reversed(st.session_state.file_history[-10:])):  # 只显示最近10个
            path = Path(file_path)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                if path.exists():
                    st.text(f"📄 {path.name}")
                    st.caption(str(path.parent))
                else:
                    st.text(f"❌ {path.name} (不存在)")
                    st.caption(str(path.parent))
            
            with col2:
                if path.exists() and st.button("选择", key=f"history_{i}"):
                    return file_path
            
            with col3:
                if st.button("移除", key=f"remove_history_{i}"):
                    st.session_state.file_history.remove(file_path)
                    st.rerun()
        
        return None
    
    def _add_to_history(self, file_path: str):
        """添加文件到历史记录"""
        if file_path in st.session_state.file_history:
            st.session_state.file_history.remove(file_path)
        
        st.session_state.file_history.append(file_path)
        
        # 限制历史记录数量
        if len(st.session_state.file_history) > 50:
            st.session_state.file_history = st.session_state.file_history[-50:]
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        import math
        
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def render_path_input_for_queue_item(self, file_name: str, file_size: int) -> Optional[str]:
        """为队列中的文件项渲染路径输入"""
        st.write(f"为文件 **{file_name}** ({self._format_file_size(file_size)}) 提供完整路径:")
        
        # 尝试智能推测路径
        suggested_paths = self._suggest_file_paths(file_name)
        
        if suggested_paths:
            st.write("💡 建议的路径:")
            selected_suggestion = st.selectbox(
                "选择建议的路径",
                ["手动输入..."] + suggested_paths,
                key=f"suggest_{file_name}_{file_size}"
            )
            
            if selected_suggestion != "手动输入...":
                return selected_suggestion
        
        # 手动输入
        manual_path = st.text_input(
            "手动输入完整路径",
            placeholder=f"例如: C:\\Users\\用户名\\Documents\\{file_name}",
            key=f"manual_{file_name}_{file_size}"
        )
        
        if manual_path:
            path = Path(manual_path)
            if path.exists() and path.is_file():
                if path.name == file_name:
                    return manual_path
                else:
                    st.warning(f"文件名不匹配: 期望 {file_name}, 实际 {path.name}")
            else:
                st.error("文件不存在或不是文件")
        
        return None
    
    def _suggest_file_paths(self, file_name: str) -> List[str]:
        """智能推测文件路径"""
        suggestions = []
        
        # 常用目录
        common_dirs = [
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path.cwd()
        ]
        
        # 在常用目录中查找同名文件
        for directory in common_dirs:
            if directory.exists():
                potential_path = directory / file_name
                if potential_path.exists():
                    suggestions.append(str(potential_path))
                
                # 也检查子目录（最多2层）
                try:
                    for subdir in directory.iterdir():
                        if subdir.is_dir():
                            potential_path = subdir / file_name
                            if potential_path.exists():
                                suggestions.append(str(potential_path))
                except (PermissionError, OSError):
                    continue
        
        # 从历史记录中查找相似的文件
        for hist_path in st.session_state.file_history:
            hist_path_obj = Path(hist_path)
            if hist_path_obj.name == file_name and hist_path_obj.exists():
                suggestions.append(hist_path)
        
        # 去重并排序
        suggestions = list(set(suggestions))
        suggestions.sort()
        
        return suggestions[:5]  # 最多返回5个建议

def render_file_selector_tab():
    """渲染文件选择器标签页"""
    # 获取或创建文件选择器实例
    if 'file_selector' not in st.session_state:
        st.session_state.file_selector = FileSelector()
    
    selector = st.session_state.file_selector
    
    st.header("📁 文件选择器")
    
    # 显示帮助信息
    with st.expander("ℹ️ 使用说明", expanded=False):
        st.markdown("""
        **文件选择器功能:**
        
        1. **拖拽上传**: 直接拖拽文件到指定区域
        2. **手动输入**: 输入完整的文件路径
        3. **文件浏览器**: 使用系统文件浏览器选择文件
        4. **常用目录**: 快速访问常用目录
        5. **历史记录**: 查看和重用之前选择的文件
        6. **智能建议**: 为拖拽的文件提供路径建议
        
        **使用步骤:**
        1. 选择一种方式添加文件到队列
        2. 为拖拽的文件设置完整路径
        3. 在"备份扫描器"中进行备份扫描
        4. 在"文件恢复器"中执行恢复操作
        """)
    
    # 文件选择方式标签
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🎯 拖拽上传", "⌨️ 手动输入", "📂 文件浏览"])
    
    with sub_tab1:
        st.subheader("🎯 拖拽文件上传")
        st.info("拖拽一个或多个文件到下方区域")
        
        # 拖拽区域
        dropped_files = selector.render_drag_drop_zone()
        
        if dropped_files:
            st.success(f"成功添加 {len(dropped_files)} 个文件到队列!")
            
            # 获取多文件处理器并添加文件
            if 'multi_file_handler' in st.session_state:
                handler = st.session_state.multi_file_handler
                handler.add_files_from_drop(dropped_files)
                st.rerun()
    
    with sub_tab2:
        st.subheader("⌨️ 手动输入文件路径")
        
        # 手动输入
        file_path = selector.render_manual_input()
        
        if file_path:
            st.success(f"文件路径已设置: {file_path}")
            # 这里可以添加到队列的逻辑
    
    with sub_tab3:
        st.subheader("📂 文件浏览器")
        
        # 文件浏览器
        selected_file = selector.render_file_browser()
        
        if selected_file:
            st.success(f"已选择文件: {selected_file}")
            # 这里可以添加到队列的逻辑
    
    # 显示常用目录
    st.subheader("📍 常用目录")
    selector.render_common_directories()
    
    # 显示文件历史
    st.subheader("📚 文件历史")
    selector.render_file_history()
    
    # 显示当前队列状态
    if 'file_queue' in st.session_state and st.session_state.file_queue:
        st.subheader("📋 当前文件队列")
        
        # 队列概览
        queue = st.session_state.file_queue
        total_files = len(queue)
        pending_paths = len([item for item in queue if not item.path])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("队列文件", total_files)
        with col2:
            st.metric("待设置路径", pending_paths)
        with col3:
            if total_files > 0:
                progress = (total_files - pending_paths) / total_files
                st.metric("完成度", f"{progress:.1%}")
        
        # 为需要路径的文件提供输入
        if pending_paths > 0:
            st.info("以下文件需要设置完整路径:")
            
            for item in queue:
                if not item.path:
                    with st.expander(f"📄 {item.name} ({selector.format_file_size(item.size)})", expanded=True):
                        
                        # 智能路径建议
                        suggestions = selector.get_intelligent_path_suggestions(item.name)
                        
                        if suggestions:
                            st.write("💡 **路径建议:**")
                            for suggestion in suggestions:
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.code(suggestion)
                                with col2:
                                    if st.button("✅ 使用", key=f"use_suggestion_{item.id}_{suggestion}"):
                                        if 'multi_file_handler' in st.session_state:
                                            handler = st.session_state.multi_file_handler
                                            if handler.add_file_path(item.id, suggestion):
                                                st.success("路径设置成功!")
                                                st.rerun()
                                            else:
                                                st.error("文件不存在!")
                        
                        # 手动输入路径
                        manual_path = selector.render_path_input_for_queue_item(item.name, item.size)
                        
                        if manual_path:
                            if 'multi_file_handler' in st.session_state:
                                handler = st.session_state.multi_file_handler
                                if handler.add_file_path(item.id, manual_path):
                                    st.success("路径设置成功!")
                                    st.rerun()
                                else:
                                    st.error("文件路径不存在!")
    else:
        st.info("📂 文件队列为空，请添加文件开始处理")
