# PowerShell执行策略修复脚本项目组Seraphiel 2025.12.02 v1.0 自动修复PowerShell执行策略以支持claude运行

import subprocess
import sys
import os

def run_command_as_admin(command):
    """以管理员身份运行命令"""
    try:
        if sys.platform == 'win32':
            # 使用runas命令以管理员身份运行
            result = subprocess.run(['powershell', '-Command', f'Start-Process powershell -ArgumentList "-Command {command}" -Verb RunAs'], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        else:
            # 非Windows系统使用sudo
            result = subprocess.run(['sudo'] + command.split(), capture_output=True, text=True, timeout=30)
            return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("命令执行超时")
        return False
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return False

def get_current_execution_policy():
    """获取当前执行策略"""
    try:
        result = subprocess.run(['powershell', '-Command', 'Get-ExecutionPolicy'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"获取执行策略时出错: {e}")
        return None

def set_execution_policy_remote_signed():
    """设置执行策略为RemoteSigned"""
    try:
        # 直接在当前进程设置执行策略
        result = subprocess.run(['powershell', '-Command', 'Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            # 如果普通权限失败，尝试管理员权限
            command = 'Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force'
            return run_command_as_admin(command)
        return True
    except Exception as e:
        print(f"设置执行策略时出错: {e}")
        return False

def test_claude_command():
    """测试claude命令是否能正常运行"""
    try:
        result = subprocess.run(['powershell', '-Command', 'claude --version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"claude命令测试成功: {result.stdout.strip()}")
            return True
        else:
            print(f"claude命令测试失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("claude命令执行超时")
        return False
    except FileNotFoundError:
        print("claude命令未找到，请确保已安装claude")
        return False
    except Exception as e:
        print(f"测试claude命令时出错: {e}")
        return False

def main():
    print("开始检查PowerShell执行策略...")
    
    # 获取当前执行策略
    current_policy = get_current_execution_policy()
    print(f"当前执行策略: {current_policy}")
    
    if current_policy == 'RemoteSigned':
        print("执行策略已经是RemoteSigned，无需修改")
    else:
        print("需要修改执行策略为RemoteSigned...")
        if set_execution_policy_remote_signed():
            print("执行策略已成功设置为RemoteSigned")
        else:
            print("设置执行策略失败，请手动以管理员身份运行PowerShell并执行:")
            print("Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned")
            return
    
    # 测试claude命令
    print("\n测试claude命令...")
    if test_claude_command():
        print("claude命令可以正常运行！")
    else:
        print("claude命令运行仍有问题，请检查claude是否已正确安装")

if __name__ == "__main__":
    main()