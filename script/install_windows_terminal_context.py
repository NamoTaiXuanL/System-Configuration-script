import winreg
import os
import subprocess


def find_windows_terminal():
    # Windows Terminal 的典型安装位置
    possible_paths = [
        # Microsoft Store 安装位置
        os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'WindowsApps', 'wt.exe'),
        # 传统安装位置
        os.path.join(os.environ['ProgramFiles'], 'Windows Terminal', 'wt.exe'),
        # 备用安装位置
        os.path.join(os.environ['ProgramFiles(x86)'], 'Windows Terminal', 'wt.exe'),
    ]
    
    # 检查每个可能的路径
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 如果以上路径都找不到，尝试在系统PATH中查找
    try:
        result = subprocess.run(['where', 'wt.exe'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # 如果还是找不到，抛出异常
    raise FileNotFoundError("未找到 Windows Terminal (wt.exe)。请确保已安装 Windows Terminal。")


def add_windows_terminal_context():
    # 在当前用户注册表下添加右键菜单（无需管理员权限）
    base_dir = r"Software\\Classes\\Directory\\shell\\OpenWindowsTerminal"
    base_bg = r"Software\\Classes\\Directory\\Background\\shell\\OpenWindowsTerminal"

    # 查找 Windows Terminal 可执行文件
    wt_path = find_windows_terminal()

    # 为“文件夹”与“文件夹背景”分别创建菜单和命令
    for menu_path, arg in [(base_dir, r'-d "%1"'), (base_bg, r'-d "%V"')]:
        # 创建菜单项键
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, menu_path, 0, winreg.KEY_WRITE)
        # 菜单显示文本
        winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, "在 Windows Terminal 中打开")
        # 设置图标为 wt.exe
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, wt_path)
        # 创建命令子键并设置启动参数
        cmd_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, menu_path + r"\\command", 0, winreg.KEY_WRITE)
        # 为避免路径解析和权限问题，显式为可执行文件加引号
        winreg.SetValueEx(cmd_key, None, 0, winreg.REG_SZ, f'"{wt_path}" {arg}')
        winreg.CloseKey(cmd_key)
        winreg.CloseKey(key)


if __name__ == "__main__":
    # 执行配置：添加两个右键菜单项
    try:
        add_windows_terminal_context()
        print("已添加 Windows Terminal 到文件夹与文件夹背景右键菜单")
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print("安装失败: 未找到 Windows Terminal")
        exit(1)
    except Exception as e:
        print(f"发生未知错误: {e}")
        exit(1)