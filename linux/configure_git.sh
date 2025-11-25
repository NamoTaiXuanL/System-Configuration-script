#!/bin/bash

# Git配置脚本 for Linux Mint 22.2
# 功能：安装Git，配置用户信息，生成SSH密钥，测试GitHub连接

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 检查是否以root权限运行
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "不建议使用root权限运行此脚本"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
}

# 检测系统信息
detect_system() {
    log_info "检测系统信息..."
    
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法检测操作系统信息"
    fi
    
    . /etc/os-release
    
    if [[ "$ID" != "linuxmint" ]]; then
        log_warning "此脚本专为Linux Mint设计，当前系统: $NAME"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
    
    log_info "操作系统: $NAME $VERSION"
    log_info "系统架构: $(uname -m)"
}

# 检查Git是否已安装
check_git_installed() {
    if command -v git &> /dev/null; then
        git_version=$(git --version | awk '{print $3}')
        log_info "Git已安装，版本: $git_version"
        return 0
    else
        log_info "Git未安装"
        return 1
    fi
}

# 安装Git
install_git() {
    log_info "安装Git..."
    
    # 更新包列表
    sudo apt update
    
    # 安装Git
    sudo apt install -y git
    
    # 验证安装
    if check_git_installed; then
        log_success "Git安装成功"
        return 0
    else
        log_error "Git安装失败"
        return 1
    fi
}

# 检查Git是否已配置用户名和邮箱
check_git_configured() {
    local user_name=""
    local user_email=""
    
    # 检查用户名
    if git config --global user.name &> /dev/null; then
        user_name=$(git config --global user.name)
    fi
    
    # 检查邮箱
    if git config --global user.email &> /dev/null; then
        user_email=$(git config --global user.email)
    fi
    
    # 两者都存在且不为空
    if [[ -n "$user_name" && -n "$user_email" ]]; then
        log_info "Git已配置 - 用户名: $user_name, 邮箱: $user_email"
        return 0
    else
        log_info "Git未配置或配置不完整"
        return 1
    fi
}

# 配置Git用户名和邮箱
configure_git() {
    log_info "配置Git用户信息..."
    
    # 检查是否已配置
    if check_git_configured; then
        read -p "Git已配置，是否重新配置？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "跳过Git配置"
            return 0
        fi
    fi
    
    # 获取用户名和邮箱
    echo "请输入Git配置信息:"
    read -p "用户名: " username
    read -p "邮箱: " email
    
    if [[ -z "$username" || -z "$email" ]]; then
        log_warning "用户名或邮箱为空，跳过配置"
        return 1
    fi
    
    # 配置Git
    git config --global user.name "$username"
    git config --global user.email "$email"
    
    # 设置一些常用配置
    git config --global core.editor "nano"
    git config --global init.defaultBranch "main"
    git config --global pull.rebase false
    
    log_success "Git配置成功"
    log_info "用户名: $(git config --global user.name)"
    log_info "邮箱: $(git config --global user.email)"
    
    return 0
}

# 检查SSH密钥是否已存在
check_ssh_key_exists() {
    local ssh_dir="$HOME/.ssh"
    local private_key="$ssh_dir/id_rsa"
    local public_key="$ssh_dir/id_rsa.pub"
    
    # 检查私钥和公钥文件是否存在
    if [[ -f "$private_key" && -f "$public_key" ]]; then
        log_info "SSH密钥已存在"
        return 0
    else
        log_info "SSH密钥不存在"
        return 1
    fi
}

# 生成SSH密钥
generate_ssh_key() {
    log_info "生成SSH密钥..."
    
    # 检查是否已存在SSH密钥
    if check_ssh_key_exists; then
        read -p "SSH密钥已存在，是否重新生成？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            # 显示现有公钥
            show_ssh_public_key
            return 0
        fi
        # 备份旧密钥
        backup_ssh_keys
    fi
    
    # 确定SSH目录
    local ssh_dir="$HOME/.ssh"
    mkdir -p "$ssh_dir"
    chmod 700 "$ssh_dir"
    
    # 生成密钥对
    local key_file="$ssh_dir/id_rsa"
    
    log_info "正在生成SSH密钥（RSA 4096位）..."
    
    # 使用ssh-keygen生成密钥
    ssh-keygen -t rsa -b 4096 -f "$key_file" -N "" -q
    
    # 设置正确的权限
    chmod 600 "$key_file"
    chmod 644 "$key_file.pub"
    
    # 读取公钥内容
    local public_key_content
    public_key_content=$(cat "$key_file.pub")
    
    log_success "SSH密钥生成成功!"
    log_info "私钥位置: $key_file"
    log_info "公钥位置: $key_file.pub"
    
    # 显示公钥内容
    echo "\n请将以下公钥内容添加到您的Git服务提供商（如GitHub、GitLab等）:"
    echo "=" * 60
    echo "$public_key_content"
    echo "=" * 60
    
    return 0
}

# 备份旧的SSH密钥
backup_ssh_keys() {
    local ssh_dir="$HOME/.ssh"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="$ssh_dir/backup_$timestamp"
    
    mkdir -p "$backup_dir"
    
    # 备份现有密钥文件
    for key_file in "$ssh_dir/id_rsa" "$ssh_dir/id_rsa.pub" "$ssh_dir/id_ed25519" "$ssh_dir/id_ed25519.pub"; do
        if [[ -f "$key_file" ]]; then
            mv "$key_file" "$backup_dir/"
        fi
    done
    
    log_info "旧SSH密钥已备份到: $backup_dir"
}

# 显示现有的SSH公钥
show_ssh_public_key() {
    local ssh_dir="$HOME/.ssh"
    local public_key_file=""
    
    # 查找公钥文件
    for key_file in "id_rsa.pub" "id_ed25519.pub"; do
        if [[ -f "$ssh_dir/$key_file" ]]; then
            public_key_file="$ssh_dir/$key_file"
            break
        fi
    done
    
    if [[ -n "$public_key_file" ]]; then
        local public_key_content
        public_key_content=$(cat "$public_key_file")
        
        echo "\n现有公钥内容:"
        echo "=" * 50
        echo "$public_key_content"
        echo "=" * 50
    else
        log_warning "未找到SSH公钥文件"
    fi
}

# 启动SSH agent并添加密钥
setup_ssh_agent() {
    log_info "设置SSH agent..."
    
    # 检查SSH agent是否已在运行
    if pgrep -u "$USER" ssh-agent > /dev/null; then
        log_info "SSH agent已在运行"
    else
        # 启动SSH agent
        eval "$(ssh-agent -s)" > /dev/null
        log_success "SSH agent已启动"
    fi
    
    # 添加SSH密钥到agent
    local ssh_dir="$HOME/.ssh"
    
    # 尝试添加常见的私钥文件
    local keys_added=0
    for key_file in "id_rsa" "id_ed25519"; do
        if [[ -f "$ssh_dir/$key_file" ]]; then
            if ssh-add "$ssh_dir/$key_file" 2>/dev/null; then
                log_info "已添加密钥: $key_file"
                keys_added=$((keys_added + 1))
            fi
        fi
    done
    
    if [[ $keys_added -gt 0 ]]; then
        log_success "SSH密钥已添加到agent"
        return 0
    else
        log_warning "未找到可用的SSH私钥文件"
        return 1
    fi
}

# 测试GitHub SSH连接
test_github_connection() {
    log_info "测试GitHub SSH连接..."
    
    # 测试SSH连接到GitHub
    local timeout=15
    
    echo "正在测试连接到GitHub..."
    
    # 使用ssh命令测试连接
    if ssh -T -o "StrictHostKeyChecking=no" -o "ConnectTimeout=$timeout" git@github.com 2>&1 | grep -q "successfully authenticated"; then
        log_success "GitHub SSH连接测试成功!"
        echo "提示: GitHub成功验证了您的SSH密钥"
        return 0
    else
        local result=$?
        if [[ $result -eq 1 ]]; then
            # GitHub返回1表示成功连接但拒绝shell访问（这是正常的）
            log_success "GitHub SSH连接测试成功!"
            echo "提示: GitHub成功验证了您的SSH密钥，但拒绝了交互式shell访问（这是正常的）"
            return 0
        else
            log_warning "GitHub连接测试失败，返回码: $result"
            echo "请确保:"
            echo "  1. 已将SSH公钥添加到GitHub"
            echo "  2. 网络连接正常"
            echo "  3. SSH密钥已正确添加到agent"
            return 1
        fi
    fi
}

# 显示使用说明
show_usage() {
    echo "使用方法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help      显示帮助信息"
    echo "  -c, --check     仅检查Git和SSH配置，不进行安装"
    echo "  -i, --install   安装Git并进行完整配置"
    echo "  -s, --ssh-only  仅配置SSH密钥（假设Git已安装）"
}

# 主函数
main() {
    local mode="install"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -c|--check)
                mode="check"
                shift
                ;;
            -i|--install)
                mode="install"
                shift
                ;;
            -s|--ssh-only)
                mode="ssh-only"
                shift
                ;;
            *)
                log_error "未知选项: $1"
                ;;
        esac
    done
    
    echo -e "${GREEN}=== Git配置脚本 for Linux Mint ===${NC}"
    echo
    
    check_root
    detect_system
    echo
    
    case "$mode" in
        "check")
            log_info "=== 检查模式 ==="
            check_git_installed
            check_git_configured
            check_ssh_key_exists
            show_ssh_public_key
            ;;
            
        "ssh-only")
            log_info "=== 仅配置SSH模式 ==="
            if ! check_git_installed; then
                log_error "Git未安装，请先安装Git或使用安装模式"
            fi
            generate_ssh_key
            setup_ssh_agent
            
            # 询问是否测试GitHub连接
            read -p "是否测试GitHub SSH连接？(y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                test_github_connection
            fi
            ;;
            
        "install")
            log_info "=== 完整安装模式 ==="
            
            # 安装Git（如果未安装）
            if ! check_git_installed; then
                install_git
            fi
            
            # 配置Git用户信息
            configure_git
            
            # 生成SSH密钥
            generate_ssh_key
            
            # 设置SSH agent
            setup_ssh_agent
            
            # 询问是否测试GitHub连接
            read -p "是否测试GitHub SSH连接？(y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                test_github_connection
            fi
            ;;
    esac
    
    echo
    log_success "配置完成!"
    echo "下一步操作建议:"
    echo "  1. 将SSH公钥添加到您的Git服务提供商"
    echo "  2. 测试Git操作: git clone, git push 等"
    echo "  3. 查看Git配置: git config --list"
}

# 执行主函数
main "$@"