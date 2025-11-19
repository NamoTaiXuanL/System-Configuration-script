# 系统配置项目组 作者Seraphiel 2025-11-20 v1.0
# 添加Python文件右键菜单"在终端中运行"功能

import winreg
import os
import sys

def add_python_terminal_context_menu():
    # 注册表路径
    python_key_path = r"Python.File\\shell\\RunInTerminal\\command"
    
    try:
        # 打开注册表键
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, python_key_path)
        
        # 获取当前Python解释器路径
        python_exe = sys.executable
        
        # 设置命令：在PowerShell中运行Python文件
        # 使用简单的调用方式
        command = f'powershell.exe -NoExit -Command "& \""{python_exe}\"" \""%1\"""'
        
        # 写入注册表值
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
        
        # 设置菜单显示名称
        shell_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "Python.File\\shell\\RunInTerminal")
        winreg.SetValueEx(shell_key, "", 0, winreg.REG_SZ, "在终端中运行")
        
        print("右键菜单添加成功！")
        print(f"命令: {command}")
        
    except Exception as e:
        print(f"添加失败: {e}")
    finally:
        winreg.CloseKey(key)
        winreg.CloseKey(shell_key)

if __name__ == "__main__":
    add_python_terminal_context_menu()