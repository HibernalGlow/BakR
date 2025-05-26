from baku.core import process  # 假设核心处理函数叫 process

def process_file(file_path: str) -> str:
    """
    处理文件，file_path 为 tauri 传入的完整路径
    """
    return process(file_path) 