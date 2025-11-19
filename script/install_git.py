import os
import subprocess
import urllib.request
import tempfile
import time


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


def main():
    """主函数"""
    # 检查是否已安装Git
    if check_git_installed():
        print("Git已经安装")
        return True
    
    # 下载安装程序
    installer_path = download_git_installer()
    if not installer_path:
        return False
    
    # 安装Git
    success = install_git(installer_path)
    
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