# Python版本检测和升级脚本

## 功能说明

这个脚本专门为Linux Mint 22.2设计，用于：
1. 检测系统中已安装的Python版本
2. 下载、编译和安装Python 3.13
3. 保持系统原有Python版本不受影响

## 脚本特性

- ✅ 自动检测系统信息和Python版本
- ✅ 安装所有必要的编译依赖包
- ✅ 从Python官方源下载最新版本
- ✅ 使用优化编译选项（--enable-optimizations）
- ✅ 创建符号链接方便使用
- ✅ 完整的错误处理和日志输出
- ✅ 颜色化输出，易于阅读

## 使用方法

### 1. 给予执行权限
```bash
chmod +x upgrade_python.sh
```

### 2. 仅检查Python版本（不安装）
```bash
./upgrade_python.sh --check
```

### 3. 安装Python 3.13
```bash
sudo ./upgrade_python.sh --install
```

或者直接运行（默认安装模式）：
```bash
sudo ./upgrade_python.sh
```

## 安装位置

- Python 3.13 将安装到: `/usr/local/bin/python3.13`
- 同时创建符号链接: `/usr/local/bin/python3`
- 系统原有的Python版本保持不变

## 依赖包

脚本会自动安装以下依赖包：
- build-essential (编译工具链)
- zlib1g-dev (压缩库)
- libncurses5-dev (终端控制)
- libssl-dev (SSL支持)
- libreadline-dev (命令行编辑)
- libsqlite3-dev (SQLite数据库)
- 以及其他必要的开发库

## 注意事项

1. **需要root权限**: 安装系统包和写入/usr/local需要sudo权限
2. **编译时间**: 编译Python可能需要10-30分钟，取决于硬件性能
3. **磁盘空间**: 需要约1-2GB的临时空间
4. **网络连接**: 需要下载约25MB的源码包
5. **系统兼容性**: 虽然专为Linux Mint 22.2设计，但也适用于其他基于Ubuntu的发行版

## 验证安装

安装完成后，可以使用以下命令验证：
```bash
/usr/local/bin/python3.13 --version
/usr/local/bin/python3 --version
```

## 卸载方法

如果需要卸载Python 3.13：
```bash
sudo rm -rf /usr/local/bin/python3.13
sudo rm -rf /usr/local/bin/python3
sudo rm -rf /usr/local/lib/python3.13*
sudo rm -rf /usr/local/include/python3.13*
```

## 故障排除

如果遇到问题：
1. 检查网络连接
2. 确保有足够的磁盘空间
3. 查看详细的错误信息输出
4. 可以尝试手动安装依赖包：`sudo apt update && sudo apt install build-essential libssl-dev zlib1g-dev`