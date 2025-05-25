# BakR - 备份文件恢复工具

基于 PyTauri 的现代化桌面应用，用于智能查找和恢复备份文件。

## 功能特性

- 🎯 **智能查找**: 拖拽任意文件，自动查找对应的 .bak/.backup/.old 文件
- 📂 **多级搜索**: 先在同级目录查找，然后向上级目录递归搜索
- 🔄 **安全恢复**: 恢复前自动将原文件备份为 .new
- 🎨 **现代界面**: 基于 PyTauri 的美观桌面界面
- 📝 **操作日志**: 记录所有操作历史
- 👀 **预览功能**: 恢复前可预览操作详情

## 安装依赖

```bash
# 安装 Python 依赖
pip install pytauri pathlib2

# 如果使用开发工具
pip install pytest black mypy
```

## 使用方法

1. 运行应用：

```bash
python src/main.py
```

1. 拖拽文件到应用窗口

1. 查看找到的备份文件

1. 确认并执行恢复操作

## 项目结构

```text
BakR/
├── src/
│   ├── main.py              # 主应用入口
│   ├── backup_finder.py     # 备份文件查找器
│   └── backup_restorer.py   # 备份恢复器
├── pyproject.toml           # 项目配置
└── README.md               # 说明文档
```

## 支持的备份文件格式

- `.bak` - 标准备份文件
- `.backup` - 备份文件
- `.old` - 旧版本文件

## 开发计划

- [ ] 添加 Tauri 前端界面
- [ ] 支持批量文件处理
- [ ] 添加配置文件支持
- [ ] 支持自定义备份文件扩展名
- [ ] 添加文件差异对比功能

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License