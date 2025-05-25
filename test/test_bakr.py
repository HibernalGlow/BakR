"""
测试脚本 - 用于测试 BakR 功能
"""
import asyncio
import sys
from pathlib import Path
import tempfile
import shutil

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from backup_finder import BackupFinder
from backup_restorer import BackupRestorer


async def test_bakr_functionality():
    """测试 BakR 的核心功能"""
    
    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print(f"测试目录: {temp_path}")
        
        # 创建测试文件
        test_file = temp_path / "test.txt"
        test_file.write_text("这是原始文件内容")
        
        # 创建备份文件
        backup_file = temp_path / "test.txt.bak"
        backup_file.write_text("这是备份文件内容")
        
        print(f"创建测试文件: {test_file}")
        print(f"创建备份文件: {backup_file}")
        
        # 初始化工具
        finder = BackupFinder()
        restorer = BackupRestorer()
        
        # 测试查找功能
        print("\n=== 测试备份文件查找 ===")
        found_backup = finder.find_nearest_backup(test_file)
        
        if found_backup:
            print(f"✅ 找到备份文件: {found_backup}")
        else:
            print("❌ 未找到备份文件")
            return
        
        # 测试搜索信息
        search_info = finder.get_search_info(test_file)
        print(f"搜索信息: {search_info}")
        
        # 测试预览功能
        print("\n=== 测试恢复预览 ===")
        preview = restorer.preview_restore(test_file, found_backup)
        print(f"预览结果: {preview}")
        
        # 测试恢复功能
        print("\n=== 测试文件恢复 ===")
        
        # 读取原始内容
        original_content = test_file.read_text()
        print(f"原始文件内容: {original_content}")
        
        # 执行恢复
        result = restorer.restore_backup(test_file, found_backup)
        
        if result["success"]:
            print(f"✅ 恢复成功: {result['message']}")
            
            # 检查恢复后的内容
            restored_content = test_file.read_text()
            print(f"恢复后内容: {restored_content}")
            
            # 检查 .new 文件是否创建
            new_file = result["details"]["new_file"]
            if new_file and Path(new_file).exists():
                new_content = Path(new_file).read_text()
                print(f"✅ .new 文件已创建: {new_file}")
                print(f".new 文件内容: {new_content}")
            else:
                print("❌ .new 文件未创建")
                
        else:
            print(f"❌ 恢复失败: {result['message']}")


if __name__ == "__main__":
    print("BakR 功能测试")
    print("=" * 50)
    
    asyncio.run(test_bakr_functionality())
    
    print("\n测试完成！")
