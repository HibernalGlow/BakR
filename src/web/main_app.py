"""
BakR - 新的主Streamlit应用
基于模块化组件的现代化备份文件恢复工具
"""
import streamlit as st
from pathlib import Path
import sys
import time

# 添加core模块路径
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

# 导入核心模块
from core.backup_finder import BackupFinder
from core.backup_restorer import BackupRestorer

# 导入UI组件
from web.components.file_selector import render_file_selector_tab
from web.components.backup_scanner import render_backup_scanner_tab
from web.components.file_restorer import render_file_restorer_tab
from web.utils.multi_file_handler import StreamlitMultiFileHandler


def load_custom_css():
    """加载自定义CSS样式"""
    css_path = Path(__file__).parent / "static" / "styles.css"
    
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def init_session_state():
    """初始化session状态"""
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = False
    
    if 'backup_finder' not in st.session_state:
        st.session_state.backup_finder = BackupFinder()
    
    if 'backup_restorer' not in st.session_state:
        st.session_state.backup_restorer = BackupRestorer()
    
    if 'multi_file_handler' not in st.session_state:
        st.session_state.multi_file_handler = StreamlitMultiFileHandler(
            st.session_state.backup_finder,
            st.session_state.backup_restorer
        )
    
    st.session_state.app_initialized = True


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/4CAF50/white?text=BakR", width=200)
        st.markdown("### 🔄 备份文件恢复工具")
        
        # 应用信息
        with st.expander("ℹ️ 关于BakR", expanded=False):
            st.markdown("""
            **BakR** 是一个智能的备份文件恢复工具，能够：
            
            - 🔍 自动扫描和匹配备份文件
            - 📁 支持多文件批量处理
            - 🎯 智能相似度分析
            - 🔄 安全的文件恢复操作
            - 📊 详细的统计报告
            
            **版本:** v2.0.0  
            **模式:** Web界面
            """)
        
        # 快速统计
        if 'file_queue' in st.session_state and st.session_state.file_queue:
            st.markdown("### 📊 快速统计")
            queue = st.session_state.file_queue
            
            total_files = len(queue)
            completed_files = len([item for item in queue if item.status.value == 'completed'])
            
            st.metric("总文件数", total_files)
            st.metric("已处理", completed_files)
            
            if total_files > 0:
                progress = completed_files / total_files
                st.progress(progress, text=f"完成度: {progress:.1%}")
        
        # 快捷操作
        st.markdown("### ⚡ 快捷操作")
        
        if st.button("🗑️ 清空队列", help="清空所有文件队列"):
            if 'multi_file_handler' in st.session_state:
                st.session_state.multi_file_handler.clear_queue()
                st.rerun()
        
        if st.button("📤 导出报告", help="导出当前状态报告"):
            if 'multi_file_handler' in st.session_state:
                report = st.session_state.multi_file_handler.export_queue_status()
                st.download_button(
                    label="💾 下载报告",
                    data=report,
                    file_name=f"bakr_report_{st.session_state.get('current_time', 'now')}.txt",
                    mime="text/plain"
                )


def render_main_content():
    """渲染主内容区域"""
    # 页面标题
    st.title("🔄 BakR - 备份文件恢复工具")
    st.markdown("现代化的多文件备份恢复解决方案")
    
    # 主要标签页
    tab1, tab2, tab3 = st.tabs(["📁 文件选择", "🔍 备份扫描", "🔄 文件恢复"])
    
    with tab1:
        render_file_selector_tab()
    
    with tab2:
        render_backup_scanner_tab()
    
    with tab3:
        render_file_restorer_tab()


def render_footer():
    """渲染页脚"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("**BakR v2.0**")
    
    with col2:
        st.markdown(
            '<div style="text-align: center;">🔄 智能备份恢复 | 🚀 快速批处理 | 📊 详细分析</div>',
            unsafe_allow_html=True
        )
    
    with col3:
        if st.button("❓ 帮助"):
            st.info("""
            **使用流程:**
            1. 在"文件选择"中添加要恢复的文件
            2. 在"备份扫描"中扫描备份文件
            3. 在"文件恢复"中执行恢复操作
            
            **技巧:**
            - 支持拖拽添加多个文件
            - 可以批量扫描和恢复
            - 查看相似度选择最佳备份
            """)


def main():
    """主函数"""
    # 页面配置
    st.set_page_config(
        page_title="BakR - 备份文件恢复工具",
        page_icon="🔄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 加载样式
    load_custom_css()
    
    # 初始化
    init_session_state()
    
    # 布局
    render_sidebar()
    render_main_content()
    render_footer()
    
    # 记录当前时间用于导出
    st.session_state.current_time = st.session_state.get('current_time', 
                                                         str(int(time.time())))


if __name__ == "__main__":
    main()
