#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import winreg
import subprocess

def install_context_menu():
    """安装右键菜单复制路径功能"""
    try:
        script_path = os.path.abspath(__file__)

        # 文件右键菜单
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r'*\\shell\\CopyPath')
        winreg.SetValue(key, None, winreg.REG_SZ, '复制路径')
        command_key = winreg.CreateKey(key, 'command')
        command = f'pythonw.exe "{script_path}" "%1"'
        winreg.SetValue(command_key, None, winreg.REG_SZ, command)

        # 文件夹右键菜单
        folder_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r'Directory\\shell\\CopyPath')
        winreg.SetValue(folder_key, None, winreg.REG_SZ, '复制路径')
        folder_command_key = winreg.CreateKey(folder_key, 'command')
        folder_command = f'pythonw.exe "{script_path}" "%1"'
        winreg.SetValue(folder_command_key, None, winreg.REG_SZ, folder_command)

        print('安装成功！')

    except Exception as e:
        print(f'安装失败: {e}')

def copy_path_to_clipboard(file_path):
    """复制路径到剪贴板"""
    try:
        # 使用cmd直接复制，不加引号
        subprocess.run(['cmd', '/c', f'echo {file_path}|clip'], check=True,
                      creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        # 备用PowerShell，隐藏窗口
        subprocess.run(['powershell', '-windowstyle', 'hidden', '-command',
                       f'Set-Clipboard -Value {file_path}'],
                      creationflags=subprocess.CREATE_NO_WINDOW)

def main():
    if len(sys.argv) > 1:
        copy_path_to_clipboard(sys.argv[1])
    else:
        install_context_menu()

if __name__ == '__main__':
    main()