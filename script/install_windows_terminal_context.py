import winreg


def add_windows_terminal_context():
    # 在当前用户注册表下添加右键菜单（无需管理员权限）
    base_dir = r"Software\\Classes\\Directory\\shell\\OpenWindowsTerminal"
    base_bg = r"Software\\Classes\\Directory\\Background\\shell\\OpenWindowsTerminal"

    # 使用 Windows Terminal 可执行文件的通用路径（支持环境变量）
    wt_path = r"%LocalAppData%\\Microsoft\\WindowsApps\\wt.exe"

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
        winreg.SetValueEx(cmd_key, None, 0, winreg.REG_SZ, f'{wt_path} {arg}')
        winreg.CloseKey(cmd_key)
        winreg.CloseKey(key)


if __name__ == "__main__":
    # 执行配置：添加两个右键菜单项
    add_windows_terminal_context()
    print("已添加 Windows Terminal 到文件夹与文件夹背景右键菜单")