# System Configuration Scripts

Windows系统配置自动化脚本集合

## 项目描述

本项目包含一系列用于自动化配置Windows系统的Python脚本，旨在简化开发环境的搭建过程。

## 功能特性

### 当前包含的脚本：

1. **install_git.py** - Git安装脚本
   - 自动下载最新版Git for Windows
   - 静默安装配置
   - 支持自动环境变量配置

2. **install_powershell.py** - PowerShell配置脚本
   - PowerShell环境优化
   - 常用模块安装
   - 配置文件设置

3. **install_windows_terminal_context.py** - Windows Terminal集成
   - 添加上下文菜单快捷方式
   - 优化终端配置

## 使用说明

### 前置要求
- Windows操作系统
- Python 3.6+
- 管理员权限（部分功能需要）

### 安装和使用

1. 克隆项目到本地：
```bash
git clone https://github.com/NamoTaiXuanL/System-Configuration-script.git
cd System-Configuration-script
```

2. 运行特定脚本：
```bash
# 安装Git
python script/install_git.py

# 配置PowerShell  
python script/install_powershell.py

# 配置Windows Terminal
python script/install_windows_terminal_context.py
```

## 项目结构

```
System-Configuration-script/
├── script/                 # 脚本目录
│   ├── install_git.py              # Git安装脚本
│   ├── install_powershell.py       # PowerShell配置脚本
│   └── install_windows_terminal_context.py  # Terminal配置脚本
├── .gitignore             # Git忽略文件
└── README.md              # 项目说明文档
```

## 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 作者

- **NamoTaiXuanL** - 项目发起者和主要维护者

## 支持

如果您遇到问题或有建议，请：
1. 查看 [Issues](https://github.com/NamoTaiXuanL/System-Configuration-script/issues) 页面
2. 创建新的Issue描述问题
3. 或通过邮件联系维护者

---

⭐ 如果这个项目对您有帮助，请给它一个Star！