# 安装器编译脚本项目组Seraphiel 2025.12.02 v1.0 编译系统配置安装器为EXE

import os
import subprocess
import shutil

def build_installer():
    """编译安装器为EXE文件"""
    print("开始编译系统配置安装器...")
    
    # 构建命令
    build_cmd = [
        "pyinstaller",
        "--name=SystemConfigInstaller",
        "--onefile",
        "--windowed",  # 不显示控制台窗口
        "--icon=NONE",  # 无图标
        "--add-data=install_python.bat;.",
        "--add-data=fix_powershell_policy.py;.",
        "--add-data=install_claude_glm.py;.",
        "--add-data=install_git.py;.",
        "system_config_installer.py"
    ]
    
    try:
        # 执行编译
        result = subprocess.run(build_cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✓ 编译成功！")
            
            # 检查生成的EXE文件
            dist_dir = os.path.join(os.path.dirname(__file__), "dist")
            exe_path = os.path.join(dist_dir, "SystemConfigInstaller.exe")
            
            if os.path.exists(exe_path):
                print(f"✓ EXE文件已生成: {exe_path}")
                print(f"✓ 文件大小: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
                return True
            else:
                print("✗ EXE文件未找到")
                return False
        else:
            print("✗ 编译失败:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ 编译过程中出错: {e}")
        return False

def cleanup_build_files():
    """清理编译产生的临时文件"""
    build_dirs = ["build", "dist", "__pycache__"]
    
    for dir_name in build_dirs:
        dir_path = os.path.join(os.path.dirname(__file__), dir_name)
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✓ 已清理: {dir_name}")
            except Exception as e:
                print(f"✗ 清理 {dir_name} 失败: {e}")

def main():
    print("=" * 60)
    print("系统配置安装器编译工具")
    print("=" * 60)
    
    # 先清理旧的编译文件
    print("\n清理旧的编译文件...")
    cleanup_build_files()
    
    # 开始编译
    print("\n开始编译...")
    success = build_installer()
    
    if success:
        print("\n✓ 编译完成！")
        print("EXE文件位置: dist/SystemConfigInstaller.exe")
    else:
        print("\n✗ 编译失败")
    
    print("=" * 60)

if __name__ == "__main__":
    main()