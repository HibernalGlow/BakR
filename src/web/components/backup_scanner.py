"""
备份扫描UI组件
纯UI展示组件，使用core模块进行业务逻辑处理
"""
import streamlit as st
import plotly.express as px
from pathlib import Path
from datetime import datetime
from typing import List
import sys

# 添加core模块路径
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from core.file_queue import FileStatus, FileQueueItem
from web.utils.multi_file_handler import StreamlitMultiFileHandler


def render_file_queue_display(handler: StreamlitMultiFileHandler):
    """渲染文件队列显示"""
    queue = st.session_state.file_queue
    
    if not queue:
        st.info("📂 文件队列为空，请先添加文件")
        return
    
    # 队列统计
    stats = st.session_state.batch_stats
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("总文件", stats['total'])
    with col2:
        st.metric("等待中", stats['pending'], 
                 delta=None if stats['pending'] == 0 else f"+{stats['pending']}")
    with col3:
        st.metric("处理中", stats['processing'])
    with col4:
        st.metric("已完成", stats['completed'], 
                 delta=None if stats['completed'] == 0 else f"+{stats['completed']}")
    with col5:
        st.metric("错误", stats['error'], 
                 delta=None if stats['error'] == 0 else f"+{stats['error']}")
    
    # 批量操作按钮
    st.subheader("🔄 批量操作")
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        if st.button("📊 批量扫描备份", 
                    disabled=st.session_state.batch_processing or stats['pending'] == 0,
                    help="扫描所有待处理文件的备份"):
            handler.batch_scan_backups()
            st.rerun()
    
    with col2:
        if st.button("🔄 批量恢复文件", 
                    disabled=st.session_state.batch_processing or stats['completed'] == 0,
                    help="恢复所有已找到备份的文件"):
            handler.batch_restore_files()
            st.rerun()
    
    with col3:
        if st.button("🗑️ 清空队列", 
                    disabled=st.session_state.batch_processing,
                    help="清空所有文件"):
            handler.clear_queue()
            st.rerun()
    
    with col4:
        if st.session_state.batch_processing:
            if st.button("⏹️ 取消", help="取消当前批量操作"):
                handler.cancel_batch_operation()
                st.rerun()
    
    # 进度条
    if st.session_state.batch_processing:
        st.progress(st.session_state.batch_progress, text="正在批量处理...")
    
    # 文件列表
    st.subheader("📁 文件队列")
    
    for i, item in enumerate(queue):
        render_file_item(handler, item, i)


def render_file_item(handler: StreamlitMultiFileHandler, item: FileQueueItem, index: int):
    """渲染单个文件项"""
    # 状态颜色映射
    status_colors = {
        FileStatus.PENDING: "🟡",
        FileStatus.PROCESSING: "🔵", 
        FileStatus.COMPLETED: "🟢",
        FileStatus.ERROR: "🔴",
        FileStatus.CANCELLED: "⚫"
    }
    
    status_icon = status_colors.get(item.status, "⚪")
    
    with st.expander(f"{status_icon} {item.name} ({handler.format_file_size(item.size)})", 
                     expanded=item.status in [FileStatus.PROCESSING, FileStatus.ERROR]):
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 文件信息
            st.write(f"**状态:** {item.status.value}")
            st.write(f"**消息:** {item.message}")
            
            if item.path:
                st.write(f"**路径:** `{item.path}`")
            else:
                # 路径输入
                path_input = st.text_input(
                    "文件完整路径:", 
                    key=f"path_{item.id}",
                    placeholder="请输入文件的完整路径"
                )
                if path_input:
                    if handler.add_file_path(item.id, path_input):
                        st.success("路径设置成功!")
                        st.rerun()
                    else:
                        st.error("文件路径不存在!")
        
        with col2:
            # 单个文件操作
            if item.path and item.status == FileStatus.PENDING:
                if st.button("📊 扫描备份", key=f"scan_{item.id}"):
                    if handler.scan_file_backups(item.id):
                        st.rerun()
            
            if st.button("🗑️ 移除", key=f"remove_{item.id}"):
                handler.remove_file(item.id)
                st.rerun()
        
        # 备份文件列表
        if item.backup_files:
            render_backup_files_list(handler, item)


def render_backup_files_list(handler: StreamlitMultiFileHandler, item: FileQueueItem):
    """渲染备份文件列表"""
    st.write("**找到的备份文件:**")
    
    for j, backup in enumerate(item.backup_files):
        backup_col1, backup_col2, backup_col3 = st.columns([3, 2, 1])
        
        with backup_col1:
            st.write(f"📄 {backup['name']}")
            st.write(f"大小: {backup['size_str']}")
            st.write(f"修改时间: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        with backup_col2:
            similarity_percent = backup['similarity'] * 100
            st.write(f"相似度: {similarity_percent:.1f}%")
            
            # 相似度进度条
            st.progress(backup['similarity'])
        
        with backup_col3:
            if st.button("🔄 恢复", key=f"restore_{item.id}_{j}"):
                if handler.restore_file(item.id, backup['path']):
                    st.success("恢复成功!")
                    st.rerun()
                else:
                    st.error("恢复失败!")
        
        st.divider()


def render_scan_statistics(handler: StreamlitMultiFileHandler):
    """渲染扫描统计信息 - 使用handler获取数据"""
    queue = st.session_state.file_queue
    if not queue:
        return
    
    st.subheader("📊 队列统计")
    
    # 使用handler获取摘要信息
    summary = handler.get_queue_summary()
    stats = summary['stats']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总文件数", summary['total_files'])
    
    with col2:
        st.metric("找到备份", stats['completed'])
    
    with col3:
        success_rate = stats['completed'] / summary['total_files'] if summary['total_files'] > 0 else 0
        st.metric("成功率", f"{success_rate:.1%}")
    
    with col4:
        st.metric("总大小", handler.format_file_size(summary['total_size']))
    
    # 状态分布图表
    render_status_distribution_chart(queue)
    
    # 文件类型分布图表  
    render_file_type_distribution_chart(queue)


def render_status_distribution_chart(queue: List[FileQueueItem]):
    """渲染状态分布图表"""
    st.subheader("📈 状态分布")
    
    # 统计状态
    status_counts = {}
    for item in queue:
        status = item.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        # 创建饼图
        fig = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title='文件状态分布',
            color_discrete_map={
                'completed': '#4caf50',
                'pending': '#ff9800', 
                'processing': '#2196f3',
                'error': '#f44336',
                'cancelled': '#9e9e9e'
            }
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def render_file_type_distribution_chart(queue: List[FileQueueItem]):
    """渲染文件类型分布图表"""
    st.subheader("📋 文件类型分布")
    
    # 统计文件类型
    type_counts = {}
    for item in queue:
        if item.path:
            file_type = item.path.suffix or '无扩展名'
        else:
            # 从文件名获取扩展名
            file_type = Path(item.name).suffix or '无扩展名'
        
        type_counts[file_type] = type_counts.get(file_type, 0) + 1
    
    if type_counts:
        # 创建条形图
        fig = px.bar(
            x=list(type_counts.keys()),
            y=list(type_counts.values()),
            title='文件类型分布',
            labels={'x': '文件类型', 'y': '数量'}
        )
        
        fig.update_layout(
            xaxis_title="文件类型",
            yaxis_title="文件数量",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_backup_scanner_tab():
    """渲染备份扫描器标签页"""
    # 获取处理器实例
    if 'multi_file_handler' not in st.session_state:
        st.error("❌ 多文件处理器未初始化")
        st.info("请先访问'文件选择'页面初始化系统")
        return
    
    handler = st.session_state.multi_file_handler
    
    st.header("🔍 备份扫描器")
    
    # 显示帮助信息
    with st.expander("ℹ️ 使用说明", expanded=False):
        st.markdown("""
        **备份扫描器功能:**
        
        1. **文件队列管理**: 查看和管理待处理的文件列表
        2. **批量扫描**: 一次性扫描所有文件的备份
        3. **单个文件操作**: 对特定文件进行扫描或恢复操作
        4. **备份信息展示**: 显示找到的备份文件详细信息
        5. **批量恢复**: 一次性恢复多个文件
        6. **统计分析**: 显示队列状态和文件类型分布
        
        **使用步骤:**
        1. 先在"文件选择"页面添加文件到队列
        2. 为每个文件设置正确的完整路径
        3. 使用"批量扫描备份"或单个文件扫描功能
        4. 查看找到的备份文件信息和统计图表
        5. 选择合适的备份进行恢复
        """)
    
    # 显示文件队列
    render_file_queue_display(handler)
      # 显示统计信息
    if st.session_state.file_queue:
        render_scan_statistics(handler)
    
    # 导出功能
    st.subheader("📤 导出队列状态")
    if st.button("📋 导出状态报告"):
        report = handler.export_queue_status()
        st.text_area("队列状态报告", report, height=300)
        
        # 下载按钮
        st.download_button(
            label="💾 下载报告",
            data=report,
            file_name=f"bakr_queue_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",            mime="text/plain"
        )
