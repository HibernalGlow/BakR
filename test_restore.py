#!/usr/bin/env python3
"""
测试 BakU 恢复功能
"""
import tempfile
import shutil
from pathlib import Path
from baku.core.backup_restorer import BackupRestorer

def test_restore_functionality():
    """测试恢复功能"""
    print("测试 BakU 恢复功能...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建测试文件
        test_file = temp_path / "test.txt"
        backup_file = temp_path / "test.txt.bak"
        
        # 写入备份文件内容
        backup_content = "这是备份文件的内容 - 应该被恢复"
        backup_file.write_text(backup_content, encoding='utf-8')
        
        # 写入目标文件内容（将被替换）
        original_content = "这是原始文件的内容 - 应该被替换"
        test_file.write_text(original_content, encoding='utf-8')
        
        print(f"备份文件: {backup_file}")
        print(f"目标文件: {test_file}")
        print(f"备份内容: {backup_content}")
        print(f"原始内容: {original_content}")
        
        # 测试恢复
        restorer = BackupRestorer()
        result = restorer.restore_backup(test_file, backup_file)
        
        print(f"恢复结果: {result}")
        
        # 检查恢复后的内容
        if test_file.exists():
            restored_content = test_file.read_text(encoding='utf-8')
            print(f"恢复后内容: {restored_content}")
            
            if restored_content == backup_content:
                print("✅ 恢复成功！内容正确")
            else:
                print("❌ 恢复失败：内容不匹配")
        else:
            print("❌ 恢复失败：目标文件不存在")
        
        # 检查备份文件是否还存在
        if backup_file.exists():
            print("✅ 备份文件保留")
        else:
            print("⚠️ 备份文件被移除")

if __name__ == "__main__":
    test_restore_functionality()
