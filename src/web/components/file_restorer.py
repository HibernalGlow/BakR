"""
文件恢复器UI组件
纯UI展示组件，使用core模块进行业务逻辑处理
"""
import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import List
import sys

# 添加core模块路径
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from core.file_queue import FileStatus, FileQueueItem
from web.utils.multi_file_handler import StreamlitMultiFileHandler


def render_restore_overview(handler: StreamlitMultiFileHandler):
    """渲染恢复概览"""
    queue = st.session_state.file_queue
    restorable_files = [
        item for item in queue 
        if item.backup_files and item.status == FileStatus.COMPLETED
    ]
    
    if not restorable_files:
        st.info("📂 没有可恢复的文件，请先在备份扫描器中扫描文件")
        return
    
    st.subheader("📋 可恢复文件概览")
    
    # 统计信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("可恢复文件", len(restorable_files))
    
    with col2:
        total_backups = sum(len(item.backup_files) for item in restorable_files)
        st.metric("总备份数", total_backups)
    
    with col3:
        total_size = sum(item.size for item in restorable_files)
        st.metric("总大小", handler.format_file_size(total_size))
    
    with col4:
        completed_restores = len([
            item for item in queue 
            if item.status == FileStatus.COMPLETED and hasattr(item, 'restored')
        ])
        st.metric("已恢复", completed_restores)
    
    # 批量恢复按钮
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 批量恢复所有文件", 
                    disabled=st.session_state.batch_processing,
                    help="使用最佳匹配的备份恢复所有文件"):
            if handler.batch_restore_files():
                st.success("批量恢复完成!")
                st.rerun()
    
    with col2:
        if st.session_state.batch_processing:
            if st.button("⏹️ 取消批量恢复", help="取消当前批量恢复操作"):
                handler.cancel_batch_operation()
                st.rerun()
    
    # 进度条
    if st.session_state.batch_processing:
        st.progress(st.session_state.batch_progress, text="正在批量恢复文件...")
    
    return restorable_files


def render_file_restore_item(handler: StreamlitMultiFileHandler, item: FileQueueItem, index: int):
    """渲染单个文件恢复项"""
    st.subheader(f"📄 {item.name}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**原文件路径:** `{item.path}`")
        st.write(f"**文件大小:** {handler.format_file_size(item.size)}")
        st.write(f"**状态:** {item.status.value}")
    
    with col2:
        # 快速恢复按钮（使用最佳匹配）
        if item.backup_files:
            best_backup = max(item.backup_files, key=lambda x: x['similarity'])
            if st.button(f"⚡ 快速恢复 (相似度: {best_backup['similarity']*100:.1f}%)", 
                        key=f"quick_restore_{item.id}"):
                if handler.restore_file(item.id, best_backup['path']):
                    st.success("恢复成功!")
                    st.rerun()
                else:
                    st.error("恢复失败!")
    
    # 备份选项
    if item.backup_files:
        st.write("**可用备份文件:**")
        
        for j, backup in enumerate(item.backup_files):
            with st.expander(f"📁 {backup['name']} (相似度: {backup['similarity']*100:.1f}%)", 
                           expanded=j == 0):  # 默认展开第一个（最佳匹配）
                
                backup_col1, backup_col2, backup_col3 = st.columns([2, 2, 1])
                
                with backup_col1:
                    st.write(f"**路径:** `{backup['path']}`")
                    st.write(f"**大小:** {backup['size_str']}")
                    st.write(f"**类型:** {backup['type']}")
                
                with backup_col2:
                    st.write(f"**修改时间:** {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # 相似度可视化
                    similarity_percent = backup['similarity'] * 100
                    st.write(f"**相似度:** {similarity_percent:.1f}%")
                    st.progress(backup['similarity'])
                    
                    # 相似度等级
                    if backup['similarity'] >= 0.9:
                        st.success("🟢 高度匹配")
                    elif backup['similarity'] >= 0.7:
                        st.warning("🟡 中等匹配")
                    else:
                        st.error("🔴 低匹配")
                
                with backup_col3:
                    # 预览按钮（如果是文本文件）
                    if backup['type'] in ['.txt', '.py', '.js', '.html', '.css', '.md']:
                        if st.button("👁️ 预览", key=f"preview_{item.id}_{j}"):
                            try:
                                with open(backup['path'], 'r', encoding='utf-8') as f:
                                    content = f.read()[:1000]  # 只显示前1000字符
                                st.code(content, language=backup['type'][1:])
                            except Exception as e:
                                st.error(f"预览失败: {str(e)}")
                    
                    # 恢复按钮
                    if st.button("🔄 恢复此备份", key=f"restore_{item.id}_{j}"):
                        if handler.restore_file(item.id, backup['path']):
                            st.success("恢复成功!")
                            st.rerun()
                        else:
                            st.error("恢复失败!")
    
    st.divider()


def render_restore_history():
    """渲染恢复历史"""
    st.subheader("📚 恢复历史")
    
    # 这里可以从session state或文件中读取恢复历史
    if 'restore_history' not in st.session_state:
        st.session_state.restore_history = []
    
    history = st.session_state.restore_history
    
    if not history:
        st.info("暂无恢复记录")
        return
    
    # 显示最近的恢复记录
    for record in reversed(history[-10:]):  # 显示最近10条
        with st.expander(f"🕐 {record['timestamp']} - {record['file_name']}", expanded=False):
            st.write(f"**原文件:** `{record['original_path']}`")
            st.write(f"**备份文件:** `{record['backup_path']}`")
            st.write(f"**状态:** {record['status']}")
            if record.get('message'):
                st.write(f"**消息:** {record['message']}")


def render_file_restorer_tab():
    """渲染文件恢复器标签页"""
    # 获取处理器实例
    if 'multi_file_handler' not in st.session_state:
        st.error("❌ 多文件处理器未初始化")
        st.info("请先访问'文件选择'页面初始化系统")
        return
    
    handler = st.session_state.multi_file_handler
    
    st.header("🔄 文件恢复器")
    
    # 显示帮助信息
    with st.expander("ℹ️ 使用说明", expanded=False):
        st.markdown("""
        **文件恢复器功能:**
        
        1. **恢复概览**: 显示所有可恢复文件的统计信息
        2. **单文件恢复**: 为每个文件选择最合适的备份进行恢复
        3. **批量恢复**: 自动选择最佳匹配的备份进行批量恢复
        4. **备份预览**: 对文本文件提供内容预览功能
        5. **恢复历史**: 查看之前的恢复操作记录
        
        **使用步骤:**
        1. 确保文件已在"备份扫描器"中找到备份
        2. 查看恢复概览了解可恢复文件情况
        3. 选择"快速恢复"或手动选择特定备份
        4. 使用"批量恢复"处理多个文件
        5. 在恢复历史中查看操作记录
        
        **相似度说明:**
        - 🟢 90%以上: 高度匹配，推荐恢复
        - 🟡 70-90%: 中等匹配，需要确认
        - 🔴 70%以下: 低匹配，谨慎恢复
        """)
    
    # 渲染恢复概览
    restorable_files = render_restore_overview(handler)
    
    if restorable_files:
        # 渲染每个可恢复文件
        st.subheader("🔧 文件恢复详情")
        
        for i, item in enumerate(restorable_files):
            render_file_restore_item(handler, item, i)
    
    # 渲染恢复历史
    render_restore_history()
