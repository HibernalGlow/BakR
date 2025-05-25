# BakR - 备份文件恢复工具

现代化的智能备份文件恢复工具，支持Web界面、命令行和TUI多种使用方式。

## 功能特性

- 🎯 **智能查找**: 自动查找对应的 .bak/.backup/.old 文件
- 📂 **多级搜索**: 先在同级目录查找，然后向上级目录递归搜索
- 🔄 **安全恢复**: 恢复前自动将原文件备份为 .new
- 🌐 **Web界面**: 基于 Streamlit 的现代化Web界面
- 💻 **多种界面**: 支持Web、命令行、TUI等多种使用方式
- 📝 **操作日志**: 记录所有操作历史
- 👀 **预览功能**: 恢复前可预览操作详情
- 📊 **统计分析**: 可视化备份文件信息和统计图表

## 安装依赖

```bash
# 使用 uv 安装（推荐）
uv install

# 或使用 pip
pip install -r requirements.txt
```

## 使用方法

### 🌐 Web界面（推荐）

最直观的使用方式，支持拖拽操作和可视化分析：

```bash
# 启动Web应用
python run_web.py

# 或直接使用streamlit
streamlit run src/web/streamlit_app.py

# 或使用批处理文件（Windows）
start_web.bat
```

然后在浏览器中访问 http://localhost:8501

**Web界面特色功能：**
- 🖱️ **直接拖拽**：从文件管理器拖拽文件到浏览器
- 📊 **可视化分析**：备份文件大小和相似度图表
- 📋 **操作历史**：完整的操作日志记录
- 🔄 **实时反馈**：操作状态和进度显示
- 📂 **文件浏览**：集成的文件选择器
- 📦 **批量处理**：支持多文件同时处理

详细使用方法请查看 [Web界面使用指南](WEB_GUIDE.md)

### 💻 命令行界面

适合快速处理和脚本自动化：

```bash
# 处理单个文件
python src/cli/cli_app.py path/to/your/file.txt

# 拖拽多个文件
python src/cli/cli_app.py file1.txt file2.py file3.doc
```

### 🖥️ TUI界面

终端用户界面，适合服务器环境：

```bash
python run_tui.py
```

## 项目结构

```text
BakR/
├── src/
│   ├── __main__.py          # 主模块入口
│   ├── backup_finder.py     # 备份文件查找器
│   ├── backup_restorer.py   # 备份恢复器
│   ├── cli/
│   │   └── cli_app.py       # 命令行界面
│   ├── tui/
│   │   ├── tui_app.py       # TUI界面
│   │   └── styles.tcss      # TUI样式
│   └── web/
│       └── streamlit_app.py # Web界面
├── run_web.py               # Web应用启动器
├── run_tui.py               # TUI应用启动器
├── start_web.bat            # Windows启动脚本
├── pyproject.toml           # 项目配置
└── README.md               # 说明文档
```

## 支持的备份文件格式

- `.bak` - 标准备份文件
- `.backup` - 备份文件
- `.old` - 旧版本文件
- 自定义扩展名（通过配置）

## 开发计划

- [x] Web界面 (Streamlit)
- [x] 命令行界面
- [x] TUI界面 (Textual)
- [x] 支持批量文件处理
- [x] 可视化统计图表
- [ ] 配置文件支持
- [ ] 支持自定义备份文件扩展名
- [ ] 添加文件差异对比功能
- [ ] Docker容器化部署

## 截图预览

### Web界面
现代化的Web界面，支持文件上传、拖拽和可视化分析。

### 命令行界面
简洁高效的命令行工具，支持批量处理和脚本集成。

## 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd BakR

# 安装依赖
uv install

# 运行测试
uv run pytest
```

## 许可证

MIT License