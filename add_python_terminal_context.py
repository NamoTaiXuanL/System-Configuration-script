# 系统配置项目组 作者Seraphiel 2025-11-20 v1.0
# 添加Python文件右键菜单"在终端中运行"功能

import winreg
import sys

def add_python_terminal_context_menu():
    python_key_path = r"Software\\Classes\\Python.File\\shell\\RunInTerminal\\command"

    key = None
    shell_key = None

    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, python_key_path)

        python_exe = sys.executable

        command = f'powershell.exe -NoExit -Command "& \"{python_exe}\" \"%1\""'

        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, command)

        shell_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\\Classes\\Python.File\\shell\\RunInTerminal")
        winreg.SetValueEx(shell_key, None, 0, winreg.REG_SZ, "在终端中运行")

        print("右键菜单添加成功！")
        print(f"命令: {command}")

    except Exception as e:
        print(f"添加失败: {e}")
    finally:
        if key:
            winreg.CloseKey(key)
        if shell_key:
            winreg.CloseKey(shell_key)

if __name__ == "__main__":
    add_python_terminal_context_menu()