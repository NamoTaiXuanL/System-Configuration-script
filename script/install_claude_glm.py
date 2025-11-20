import os
import subprocess
import urllib.request
import tempfile
import sys

def is_node_installed(min_major=18):
    print("检测 Node.js 安装状态...")
    try:
        r = subprocess.run(["node", "-v"], capture_output=True, text=True, timeout=5)
        if r.returncode != 0:
            print("未检测到 Node.js")
            return False
        v = r.stdout.strip().lstrip("v")
        major = int(v.split(".")[0])
        ok = major >= min_major
        print(f"当前 Node.js 版本: v{v} -> {'满足要求' if ok else '版本过低'}")
        return ok
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        print("未检测到 Node.js")
        return False

def download_node_installer(version="20.17.0"):
    print("下载 Node.js 安装程序...")
    url = f"https://nodejs.org/dist/v{version}/node-v{version}-x64.msi"
    path = os.path.join(tempfile.gettempdir(), f"node-v{version}-x64.msi")
    try:
        urllib.request.urlretrieve(url, path)
        print(f"下载完成: {path}")
        return path
    except Exception as e:
        print(f"下载失败: {e}")
        return None

def install_node(msi_path):
    if not msi_path or not os.path.exists(msi_path):
        print("安装程序不存在")
        return False
    print("静默安装 Node.js...")
    try:
        r = subprocess.run(["msiexec", "/i", msi_path, "/qn", "/norestart"], capture_output=True, text=True)
        if r.returncode == 0:
            print("Node.js 安装成功")
            return True
        print(f"安装失败，返回码: {r.returncode}")
        print(r.stderr)
        return False
    except Exception as e:
        print(f"安装过程中出错: {e}")
        return False

def get_roaming_npm_path():
    appdata = os.environ.get("APPDATA")
    if appdata:
        return os.path.join(appdata, "npm")
    return os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm")

def ensure_node_path():
    node_path = r"C:\\Program Files\\nodejs"
    npm_roam = get_roaming_npm_path()
    print("确保 Node.js 与 npm 路径在环境变量 PATH 中...")
    current = os.environ.get("PATH", "")
    add_list = []
    if os.path.exists(node_path) and node_path not in current:
        add_list.append(node_path)
    if os.path.exists(npm_roam) and npm_roam not in current:
        add_list.append(npm_roam)
    if add_list:
        new_path = current + (os.pathsep + os.pathsep.join(add_list) if current else os.pathsep.join(add_list))
        try:
            subprocess.run(["setx", "PATH", new_path], check=False, shell=True)
            os.environ["PATH"] = new_path
            for p in add_list:
                print(f"已添加路径: {p}")
        except Exception as e:
            print(f"添加 PATH 失败: {e}")
    else:
        print("PATH 已包含所需路径或路径不存在")

def find_npm_cmd():
    candidates = [
        os.path.join(r"C:\\Program Files\\nodejs", "npm.cmd"),
        os.path.join(get_roaming_npm_path(), "npm.cmd"),
        "npm",
    ]
    for c in candidates:
        if c == "npm":
            return c
        if os.path.exists(c):
            return c
    return "npm"

def find_claude_cmd():
    candidates = [
        os.path.join(get_roaming_npm_path(), "claude.cmd"),
        os.path.join(get_roaming_npm_path(), "claude.ps1"),
        "claude",
    ]
    for c in candidates:
        if c == "claude":
            return c
        if os.path.exists(c):
            return c
    return "claude"

def install_claude_code():
    print("安装 Claude Code...")
    try:
        npm_cmd = find_npm_cmd()
        nr = subprocess.run(f'"{npm_cmd}" -v' if npm_cmd != "npm" else "npm -v", capture_output=True, text=True, shell=True)
        if nr.returncode != 0:
            print("未检测到 npm，请确认 Node.js 已正确安装")
            return False
        ir = subprocess.run(
            f'"{npm_cmd}" install -g @anthropic-ai/claude-code' if npm_cmd != "npm" else "npm install -g @anthropic-ai/claude-code",
            text=True,
            shell=True,
        )
        if ir.returncode != 0:
            print("Claude Code 安装失败")
            return False
        ensure_node_path()
        print("尝试定位 claude 命令...")
        try:
            loc = subprocess.run("where claude", capture_output=True, text=True, shell=True)
            if loc.stdout.strip():
                print(loc.stdout.strip())
        except Exception:
            pass
        claude_cmd = find_claude_cmd()
        if os.path.exists(claude_cmd):
            vr = subprocess.run([claude_cmd, "--version"], capture_output=True, text=True)
        else:
            vr = subprocess.run("claude --version", capture_output=True, text=True, shell=True)
        if vr.returncode == 0:
            print(f"Claude Code 版本: {vr.stdout.strip()}")
            return True
        print("Claude Code 验证失败")
        return False
    except Exception as e:
        print(f"安装 Claude Code 出错: {e}")
        return False

def configure_glm_env(api_key=None):
    print("配置 GLM 环境变量...")
    base_url = "https://open.bigmodel.cn/api/anthropic"
    try:
        subprocess.run(["setx", "ANTHROPIC_BASE_URL", base_url], check=False, shell=True)
        print(f"已设置 ANTHROPIC_BASE_URL = {base_url}")
    except Exception as e:
        print(f"设置 ANTHROPIC_BASE_URL 失败: {e}")
    key = api_key
    if not key:
        try:
            key = input("请输入智谱 API Key(留空跳过): ").strip()
        except Exception:
            key = ""
    if key:
        try:
            subprocess.run(["setx", "ANTHROPIC_AUTH_TOKEN", key], check=False, shell=True)
            print("已设置 ANTHROPIC_AUTH_TOKEN")
        except Exception as e:
            print(f"设置 ANTHROPIC_AUTH_TOKEN 失败: {e}")
    else:
        print("未提供 API Key，跳过设置 ANTHROPIC_AUTH_TOKEN")

def guide_glm_coding_plan():
    print("GLM Coding Plan 引导:")
    print("1) 访问 https://open.bigmodel.cn 注册并获取 API Key")
    print("2) 参考文档: https://docs.bigmodel.cn/cn/guide/develop/claude")
    print("3) 启动终端运行 'claude'，遇到提示选择使用该 API Key")

def run_git_setup():
    print("安装/配置 Git for Windows...")
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.append(here)
        from install_git import main as git_main
        git_main()
    except Exception as e:
        print(f"Git 配置调用失败: {e}")

def main():
    print("=" * 50)
    print("Win10/11 自动安装 Claude Code 与配置 GLM API")
    print("=" * 50)

    ensure_node_path()
    node_ok = is_node_installed()
    if not node_ok:
        msi = download_node_installer()
        if msi and install_node(msi):
            ensure_node_path()
        else:
            print("Node.js 安装失败，请以管理员身份重试")

    run_git_setup()

    if install_claude_code():
        print("Claude Code 安装完成")
    else:
        print("Claude Code 安装未完成")

    configure_glm_env()
    guide_glm_coding_plan()

    print("=" * 50)
    print("操作完成，请重新打开终端以使环境变量生效")
    print("在任意项目目录运行 'claude' 即可使用")

if __name__ == "__main__":
    main()