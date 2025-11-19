import os
import subprocess
import urllib.request
import tempfile
import time
import getpass
import shutil


def download_git_installer():
    """下载Git安装程序"""
    git_url = "https://github.com/git-for-windows/git/releases/download/v2.52.0.windows.1/Git-2.52.0-64-bit.exe"
    
    # 创建临时文件
    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, "Git-2.52.0-64-bit.exe")
    
    print("正在下载Git安装程序...")
    
    # 下载文件
    try:
        urllib.request.urlretrieve(git_url, installer_path)
        print(f"下载完成: {installer_path}")
        return installer_path
    except Exception as e:
        print(f"下载失败: {e}")
        return None


def install_git(installer_path):
    """静默安装Git"""
    if not installer_path or not os.path.exists(installer_path):
        print("安装程序不存在")
        return False
    
    print("正在安装Git...")
    
    # 使用静默安装参数
    try:
        process = subprocess.Popen([
            installer_path,
            "/VERYSILENT",
            "/NORESTART",
            "/NOCANCEL",
            "/SP-",
            "/CLOSEAPPLICATIONS",
            "/FORCECLOSEAPPLICATIONS"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待安装完成
        process.wait()
        
        if process.returncode == 0:
            print("Git安装成功")
            return True
        else:
            print(f"安装失败，返回码: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"安装过程中出错: {e}")
        return False


def check_git_installed():
    """检查Git是否已安装"""
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_git_configured():
    """检查Git是否已配置用户名和邮箱"""
    try:
        # 检查用户名
        result_name = subprocess.run(['git', 'config', '--global', 'user.name'], 
                                   capture_output=True, text=True, timeout=5)
        # 检查邮箱
        result_email = subprocess.run(['git', 'config', '--global', 'user.email'], 
                                    capture_output=True, text=True, timeout=5)
        
        # 两者都存在且不为空
        return (result_name.returncode == 0 and result_name.stdout.strip() and
                result_email.returncode == 0 and result_email.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_ssh_key_exists():
    """检查SSH密钥是否已存在"""
    ssh_dir = os.path.join(os.path.expanduser('~'), '.ssh')
    private_key = os.path.join(ssh_dir, 'id_rsa')
    public_key = os.path.join(ssh_dir, 'id_rsa.pub')
    
    # 检查私钥和公钥文件是否存在
    return os.path.exists(private_key) and os.path.exists(public_key)


def configure_git():
    """配置Git用户名和邮箱"""
    print("\n=== Git配置 ===")
    
    # 检查是否已配置
    if check_git_configured():
        print("Git用户名和邮箱已配置，跳过")
        return
    
    # 询问用户是否要配置
    choice = input("是否要配置Git用户名和邮箱? (y/n, 默认y): ").strip().lower()
    if choice == 'n':
        print("跳过Git配置")
        return
    
    # 获取用户名和邮箱
    username = input("请输入Git用户名: ").strip()
    email = input("请输入Git邮箱: ").strip()
    
    if username and email:
        try:
            subprocess.run(['git', 'config', '--global', 'user.name', username], check=True)
            subprocess.run(['git', 'config', '--global', 'user.email', email], check=True)
            print("Git用户名和邮箱配置成功")
        except subprocess.CalledProcessError as e:
            print(f"Git配置失败: {e}")
    else:
        print("用户名或邮箱为空，跳过配置")


def generate_ssh_key():
    """生成SSH密钥"""
    print("\n=== SSH密钥配置 ===")
    
    # 检查是否已存在SSH密钥
    if check_ssh_key_exists():
        print("SSH密钥已存在，跳过生成")
        # 读取现有公钥内容
        pub_key_file = os.path.join(os.path.expanduser('~'), '.ssh', 'id_rsa.pub')
        if os.path.exists(pub_key_file):
            with open(pub_key_file, 'r') as f:
                public_key = f.read().strip()
            print(f"\n现有公钥内容:")
            print("=" * 50)
            print(public_key)
            print("=" * 50)
            return public_key
        return None
    
    # 询问用户是否要生成SSH密钥
    choice = input("是否要生成SSH密钥? (y/n, 默认y): ").strip().lower()
    if choice == 'n':
        print("跳过SSH密钥生成")
        return None
    
    # 确定SSH目录
    ssh_dir = os.path.join(os.path.expanduser('~'), '.ssh')
    os.makedirs(ssh_dir, exist_ok=True)
    
    # 生成密钥对
    key_file = os.path.join(ssh_dir, 'id_rsa')
    
    try:
        # 生成SSH密钥
        result = subprocess.run([
            'ssh-keygen', '-t', 'rsa', '-b', '4096', 
            '-f', key_file, '-N', '', '-q'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # 读取公钥内容
            pub_key_file = key_file + '.pub'
            if os.path.exists(pub_key_file):
                with open(pub_key_file, 'r') as f:
                    public_key = f.read().strip()
                
                print(f"\nSSH密钥生成成功!")
                print(f"私钥位置: {key_file}")
                print(f"公钥位置: {pub_key_file}")
                print(f"\n请将以下公钥内容添加到您的Git服务提供商:")
                print("=" * 50)
                print(public_key)
                print("=" * 50)
                
                return public_key
        else:
            print("SSH密钥生成失败")
            
    except Exception as e:
        print(f"SSH密钥生成过程中出错: {e}")
    
    return None


def setup_ssh_agent():
    """设置SSH agent - Windows专用版本"""
    try:
        # Windows系统使用服务方式启动ssh-agent
        print("正在设置SSH agent服务...")
        
        # 1. 设置服务为手动启动
        result1 = subprocess.run([
            'powershell', '-Command', 
            'Set-Service -Name ssh-agent -StartupType Manual'
        ], capture_output=True, text=True, timeout=10)
        
        # 2. 启动ssh-agent服务
        result2 = subprocess.run([
            'powershell', '-Command', 
            'Start-Service ssh-agent'
        ], capture_output=True, text=True, timeout=10)
        
        # 3. 检查服务状态
        result3 = subprocess.run([
            'powershell', '-Command', 
            'Get-Service ssh-agent | Select-Object Status'
        ], capture_output=True, text=True, timeout=10)
        
        if result2.returncode == 0 and 'Running' in result3.stdout:
            # 4. 添加SSH密钥到agent
            result4 = subprocess.run([
                'ssh-add', os.path.join(os.path.expanduser('~'), '.ssh', 'id_rsa')
            ], capture_output=True, text=True, timeout=10)
            
            if result4.returncode == 0:
                print("SSH agent设置完成，密钥已添加")
            else:
                print("SSH密钥添加失败，请手动运行: ssh-add ~/.ssh/id_rsa")
        else:
            # 如果服务启动失败，提供详细的手动指导
            print("SSH agent服务启动失败，请手动执行以下PowerShell命令:")
            print("1. 设置服务启动类型: Set-Service -Name ssh-agent -StartupType Manual")
            print("2. 启动服务: Start-Service ssh-agent")
            print("3. 检查服务状态: Get-Service ssh-agent")
            print("4. 添加SSH密钥: ssh-add ~/.ssh/id_rsa")
            
    except subprocess.TimeoutExpired:
        print("SSH agent操作超时，请手动配置")
    except subprocess.CalledProcessError as e:
        print(f"SSH agent设置失败: {e}")
    except Exception as e:
        print(f"SSH agent设置过程中出错: {e}")


def add_git_to_path():
    """添加Git安装路径到环境变量"""
    print("添加Git到系统环境变量...")
    
    # Git的默认安装路径
    git_paths = [
        os.path.join(os.environ['ProgramFiles'], 'Git', 'bin'),
        os.path.join(os.environ['ProgramFiles'], 'Git', 'cmd'),
        os.path.join(os.environ['ProgramFiles(x86)'], 'Git', 'bin'),
        os.path.join(os.environ['ProgramFiles(x86)'], 'Git', 'cmd')
    ]
    
    # 获取当前PATH
    current_path = os.environ.get('PATH', '')
    
    # 添加Git路径到PATH
    for git_path in git_paths:
        if os.path.exists(git_path) and git_path not in current_path:
            os.environ['PATH'] = current_path + os.pathsep + git_path
            print(f"已添加路径: {git_path}")
    
    return True


def main():
    """主函数"""
    # 检查是否已安装Git
    if check_git_installed():
        print("Git已经安装")
        # 即使已安装，也提供配置选项
        configure_git()
        generate_ssh_key()
        return True
    
    # 下载安装程序
    installer_path = download_git_installer()
    if not installer_path:
        return False
    
    # 安装Git
    success = install_git(installer_path)
    
    if success:
        # 添加Git到环境变量
        add_git_to_path()
        # Git安装成功后进行配置
        configure_git()
        public_key = generate_ssh_key()
        if public_key:
            setup_ssh_agent()
    
    # 清理临时文件
    try:
        if os.path.exists(installer_path):
            os.remove(installer_path)
    except:
        pass
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)