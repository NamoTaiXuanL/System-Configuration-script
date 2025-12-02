import os
import zipfile
import requests
import tempfile
import shutil
import subprocess
import sys

def download_file(url, save_path):
    """下载文件"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def extract_zip(zip_path, extract_to):
    """解压ZIP文件"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def add_to_path(new_path):
    """添加路径到系统环境变量"""
    # 获取当前PATH
    current_path = os.environ.get('PATH', '')
    
    # 如果路径不在PATH中，则添加
    if new_path not in current_path:
        new_path_value = current_path + os.pathsep + new_path
        
        # 使用setx命令永久设置环境变量
        subprocess.run(['setx', 'PATH', new_path_value], check=True, shell=True)
        
        # 同时设置当前进程的PATH
        os.environ['PATH'] = new_path_value

def set_default_powershell(pwsh_path):
    """设置PowerShell 7为默认终端"""
    print("正在设置PowerShell 7为默认终端...")
    
    # 获取pwsh.exe所在目录
    pwsh_dir = os.path.dirname(pwsh_path)
    
    try:
        # 方法1: 修改注册表设置默认终端
        # 设置PowerShell Core为默认Shell
        reg_commands = [
            ['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Terminal\\', '/v', 'DefaultProfile', '/t', 'REG_SZ', '/d', '{574e775e-4f2a-5b96-ac1e-a2962a402336}', '/f'],
            ['reg', 'add', 'HKCU\\Console\\%SystemRoot%_System32_WindowsPowerShell_v1.0_powershell.exe', '/v', 'FaceName', '/t', 'REG_SZ', '/d', 'Cascadia Code', '/f'],
            ['reg', 'add', 'HKCU\\Console\\%SystemRoot%_System32_WindowsPowerShell_v1.0_powershell.exe', '/v', 'FontFamily', '/t', 'REG_DWORD', '/d', '0x36', '/f']
        ]
        
        for cmd in reg_commands:
            subprocess.run(cmd, capture_output=True, text=True)
        
        # 方法2: 创建快捷方式到用户目录
        startup_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        shortcut_path = os.path.join(startup_dir, 'PowerShell 7.lnk')
        
        # 使用PowerShell创建快捷方式
        ps_script = f'''
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{pwsh_path}"
        $Shortcut.WorkingDirectory = "%USERPROFILE%"
        $Shortcut.Save()
        '''
        
        subprocess.run(['powershell', '-Command', ps_script], capture_output=True)
        
        print("PowerShell 7已设置为默认终端")
        print("快捷方式已创建到开始菜单")
        
    except Exception as e:
        print(f"设置默认终端时出错: {e}")
        print("您可以手动将PowerShell 7设置为默认终端:")
        print("1. 右键点击任务栏")
        print("2. 选择'终端设置'")
        print("3. 将默认终端应用程序设置为'PowerShell'")

def install_windows_terminal():
    """安装Windows Terminal"""
    terminal_url = "https://github.com/microsoft/terminal/releases/download/v1.23.12811.0/Microsoft.WindowsTerminal_1.23.12811.0_x64.zip"
    
    print("正在安装Windows Terminal...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "terminal.zip")
        extract_path = os.path.join(temp_dir, "terminal")
        
        print("正在下载Windows Terminal...")
        download_file(terminal_url, zip_path)
        
        print("正在解压文件...")
        extract_zip(zip_path, extract_path)
        
        # 找到解压后的主目录
        extracted_contents = os.listdir(extract_path)
        if len(extracted_contents) == 1:
            terminal_dir = os.path.join(extract_path, extracted_contents[0])
        else:
            terminal_dir = extract_path
        
        # 目标安装目录 - 安装到Program Files
        install_dir = os.path.join(os.environ['ProgramFiles'], "Windows Terminal")
        
        print(f"正在安装到: {install_dir}")
        
        # 如果目标目录已存在，先删除
        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)
        
        # 移动文件到安装目录
        shutil.copytree(terminal_dir, install_dir)
        
        # 注册Windows Terminal
        register_windows_terminal(install_dir)
        
        print("Windows Terminal安装完成!")
        print(f"已安装到: {install_dir}")

def register_windows_terminal(install_dir):
    """注册Windows Terminal到系统"""
    print("正在注册Windows Terminal...")
    
    try:
        # 查找主要的可执行文件
        wt_exe_path = None
        for root, dirs, files in os.walk(install_dir):
            if "WindowsTerminal.exe" in files:
                wt_exe_path = os.path.join(root, "WindowsTerminal.exe")
                break
        
        if wt_exe_path:
            # 创建开始菜单快捷方式
            startup_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs')
            shortcut_path = os.path.join(startup_dir, 'Windows Terminal.lnk')
            
            # 使用PowerShell创建快捷方式
            ps_script = f'''
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "{wt_exe_path}"
            $Shortcut.WorkingDirectory = "%USERPROFILE%"
            $Shortcut.Save()
            '''
            
            subprocess.run(['powershell', '-Command', ps_script], capture_output=True)
            
            # 添加到注册表
            reg_commands = [
                ['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\WindowsTerminal.exe', '/ve', '/t', 'REG_SZ', '/d', f'"{wt_exe_path}"', '/f'],
                ['reg', 'add', 'HKCU\\Software\\Classes\\wt', '/ve', '/t', 'REG_SZ', '/d', 'URL:Windows Terminal Protocol', '/f'],
                ['reg', 'add', 'HKCU\\Software\\Classes\\wt', '/v', 'URL Protocol', '/t', 'REG_SZ', '/d', '', '/f'],
                ['reg', 'add', 'HKCU\\Software\\Classes\\wt\\shell\\open\\command', '/ve', '/t', 'REG_SZ', '/d', f'"{wt_exe_path}"', '/f']
            ]
            
            for cmd in reg_commands:
                subprocess.run(cmd, capture_output=True, text=True)
            
            print("Windows Terminal已成功注册到系统")
        else:
            print("警告: 未找到WindowsTerminal.exe")
            
    except Exception as e:
        print(f"注册Windows Terminal时出错: {e}")

def is_powershell_installed():
    """检测是否已安装PowerShell 7"""
    install_dir = os.path.join(os.environ['ProgramFiles'], "PowerShell", "7")
    
    # 检查安装目录是否存在
    if not os.path.exists(install_dir):
        return False
    
    # 检查pwsh.exe是否存在
    pwsh_path = None
    for root, dirs, files in os.walk(install_dir):
        if "pwsh.exe" in files:
            pwsh_path = os.path.join(root, "pwsh.exe")
            break
    
    if not pwsh_path or not os.path.exists(pwsh_path):
        return False
    
    # 验证PowerShell是否能正常运行
    try:
        result = subprocess.run([pwsh_path, "--version"], 
                             capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def is_windows_terminal_installed():
    """检测是否已安装Windows Terminal"""
    install_dir = os.path.join(os.environ['ProgramFiles'], "Windows Terminal")
    
    # 检查安装目录是否存在
    if not os.path.exists(install_dir):
        return False
    
    # 检查WindowsTerminal.exe是否存在
    wt_exe_path = None
    for root, dirs, files in os.walk(install_dir):
        if "WindowsTerminal.exe" in files:
            wt_exe_path = os.path.join(root, "WindowsTerminal.exe")
            break
    
    return wt_exe_path and os.path.exists(wt_exe_path)

def main():
    """主函数"""
    
    # 显示欢迎信息
    print("=" * 50)
    print("PowerShell 7 和 Windows Terminal 自动安装程序")
    print("=" * 50)
    
    # 检查管理员权限
    try:
        # 尝试在Program Files创建目录来检查权限
        test_dir = os.path.join(os.environ['ProgramFiles'], "test_powershell_install")
        os.makedirs(test_dir, exist_ok=True)
        shutil.rmtree(test_dir)
    except PermissionError:
        print("错误: 需要管理员权限才能安装到Program Files目录")
        print("请以管理员身份运行此脚本:")
        print("1. 右键点击命令提示符或PowerShell")
        print("2. 选择'以管理员身份运行'")
        print("3. 然后运行: python install_powershell.py")
        return
    
    # 自动检测并安装PowerShell 7
    print("\n检测PowerShell 7安装状态...")
    if is_powershell_installed():
        print("✓ PowerShell 7 已安装，跳过安装")
    else:
        print("开始安装 PowerShell 7")
        print("=" * 30)
        
        powershell_url = "https://github.com/PowerShell/PowerShell/releases/download/v7.5.4/PowerShell-7.5.4-win-x64.zip"
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "powershell.zip")
            extract_path = os.path.join(temp_dir, "powershell")
            
            print("正在下载PowerShell...")
            download_file(powershell_url, zip_path)
            
            print("正在解压文件...")
            extract_zip(zip_path, extract_path)
            
            # 找到解压后的主目录
            extracted_contents = os.listdir(extract_path)
            if len(extracted_contents) == 1:
                powershell_dir = os.path.join(extract_path, extracted_contents[0])
            else:
                powershell_dir = extract_path
            
            # 目标安装目录
            install_dir = os.path.join(os.environ['ProgramFiles'], "PowerShell", "7")
            
            print(f"正在安装到: {install_dir}")
            
            # 如果目标目录已存在，先删除
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            
            # 移动文件到安装目录
            shutil.copytree(powershell_dir, install_dir)
            
            # 添加bin目录到PATH
            bin_path = os.path.join(install_dir, "bin")
            add_to_path(bin_path)
            
            print("PowerShell 7安装完成!")
    
    # 自动检测并安装Windows Terminal
    print("\n检测Windows Terminal安装状态...")
    if is_windows_terminal_installed():
        print("✓ Windows Terminal 已安装，跳过安装")
    else:
        print("开始安装 Windows Terminal")
        print("=" * 30)
        install_windows_terminal()
    
    # 最终验证
    print("\n" + "=" * 50)
    print("安装验证:")
    print("=" * 50)
    
    if is_powershell_installed():
        print("✓ PowerShell 7 安装成功")
        
        # 设置PowerShell 7为默认终端
        install_dir = os.path.join(os.environ['ProgramFiles'], "PowerShell", "7")
        pwsh_path = None
        for root, dirs, files in os.walk(install_dir):
            if "pwsh.exe" in files:
                pwsh_path = os.path.join(root, "pwsh.exe")
                break
        
        if pwsh_path:
            set_default_powershell(pwsh_path)
    else:
        print("✗ PowerShell 7 安装失败")
    
    if is_windows_terminal_installed():
        print("✓ Windows Terminal 安装成功")
    else:
        print("✗ Windows Terminal 安装失败")
    
    print("\n请重新启动终端以使环境变量生效")

if __name__ == "__main__":
    main()