#!/bin/bash

# Claude+GLM配置脚本 for Linux Mint 22.2
# 功能：安装Node.js, Claude Code, 配置GLM API环境

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

# 检查Node.js是否已安装
is_node_installed() {
    local min_major=18
    log_info "检测 Node.js 安装状态..."
    
    if command -v node &> /dev/null; then
        local version
        version=$(node -v 2>/dev/null | sed 's/^v//')
        if [[ -n "$version" ]]; then
            local major
            major=$(echo "$version" | cut -d. -f1)
            local ok=$((major >= min_major))
            log_info "当前 Node.js 版本: v$version -> $(if [ $ok -eq 1 ]; then echo '满足要求'; else echo '版本过低'; fi)"
            return $((ok == 1 ? 0 : 1))
        fi
    fi
    
    log_info "未检测到 Node.js"
    return 1
}

# 安装Node.js
install_node() {
    log_info "安装 Node.js..."
    
    # 更新包列表
    sudo apt update
    
    # 安装Node.js和npm
    sudo apt install -y nodejs npm
    
    # 验证安装
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        log_success "Node.js 安装成功"
        log_info "Node.js 版本: $(node -v)"
        log_info "npm 版本: $(npm -v)"
        return 0
    else
        log_error "Node.js 安装失败"
        return 1
    fi
}

# 检查Git是否已安装
check_git_installed() {
    if command -v git &> /dev/null; then
        log_info "Git已安装，版本: $(git --version | awk '{print $3}')"
        return 0
    else
        log_info "Git未安装"
        return 1
    fi
}

# 安装Git
install_git() {
    log_info "安装 Git..."
    
    sudo apt update
    sudo apt install -y git
    
    if check_git_installed; then
        log_success "Git安装成功"
        return 0
    else
        log_error "Git安装失败"
        return 1
    fi
}

# 安装Claude Code
install_claude_code() {
    log_info "安装 Claude Code..."
    
    # 检查npm是否可用
    if ! command -v npm &> /dev/null; then
        log_error "npm 未找到，请先安装 Node.js"
        return 1
    fi
    
    # 安装Claude Code全局包
    if sudo npm install -g @anthropic-ai/claude-code; then
        log_success "Claude Code 安装成功"
        
        # 验证安装
        if command -v claude &> /dev/null; then
            local version
            version=$(claude --version 2>/dev/null)
            if [[ -n "$version" ]]; then
                log_info "Claude Code 版本: $version"
                return 0
            fi
        fi
        
        log_warning "Claude Code 安装完成，但可能需要重新登录或重启终端"
        return 0
    else
        log_error "Claude Code 安装失败"
        return 1
    fi
}

# 配置GLM环境变量
configure_glm_env() {
    local api_key=""
    local base_url="https://open.bigmodel.cn/api/anthropic"
    
    log_info "配置 GLM 环境变量..."
    
    # 设置ANTHROPIC_BASE_URL
    if ! grep -q "ANTHROPIC_BASE_URL" ~/.bashrc; then
        echo "export ANTHROPIC_BASE_URL=$base_url" >> ~/.bashrc
        log_info "已设置 ANTHROPIC_BASE_URL = $base_url"
    else
        log_info "ANTHROPIC_BASE_URL 已配置"
    fi
    
    # 获取API Key
    read -p "请输入智谱 API Key(留空跳过): " api_key
    api_key=$(echo "$api_key" | tr -d '[:space:]')
    
    if [[ -n "$api_key" ]]; then
        if ! grep -q "ANTHROPIC_AUTH_TOKEN" ~/.bashrc; then
            echo "export ANTHROPIC_AUTH_TOKEN=$api_key" >> ~/.bashrc
            log_info "已设置 ANTHROPIC_AUTH_TOKEN"
        else
            log_info "ANTHROPIC_AUTH_TOKEN 已配置"
        fi
    else
        log_info "未提供 API Key，跳过设置 ANTHROPIC_AUTH_TOKEN"
    fi
    
    # 应用环境变量到当前会话
    export ANTHROPIC_BASE_URL="$base_url"
    if [[ -n "$api_key" ]]; then
        export ANTHROPIC_AUTH_TOKEN="$api_key"
    fi
}

# 引导GLM Coding Plan
guide_glm_coding_plan() {
    echo "\n=== GLM Coding Plan 引导 ==="
    echo "1) 访问 https://open.bigmodel.cn 注册并获取 API Key"
    echo "2) 参考文档: https://docs.bigmodel.cn/cn/guide/develop/claude"
    echo "3) 启动终端运行 'claude'，遇到提示选择使用该 API Key"
    echo "4) 支持的模型:"
    echo "   - GLM-4.6 (默认用于复杂任务)"
    echo "   - GLM-4.5-Air (轻量任务自动路由)"
    echo "5) 配置位置: ~/.claude/settings.json"
    echo
}

# 创建Claude配置文件
create_claude_config() {
    local config_dir="$HOME/.claude"
    local config_file="$config_dir/settings.json"
    
    mkdir -p "$config_dir"
    
    if [[ ! -f "$config_file" ]]; then
        cat > "$config_file" << 'EOF'
{
  "env": {
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.6",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.6"
  }
}
EOF
        log_info "创建 Claude 配置文件: $config_file"
    else
        log_info "Claude 配置文件已存在: $config_file"
    fi
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    local success=0
    
    # 检查Node.js
    if is_node_installed; then
        log_success "✓ Node.js 安装验证通过"
    else
        log_error "✗ Node.js 安装验证失败"
        success=1
    fi
    
    # 检查Git
    if check_git_installed; then
        log_success "✓ Git 安装验证通过"
    else
        log_error "✗ Git 安装验证失败"
        success=1
    fi
    
    # 检查Claude Code
    if command -v claude &> /dev/null; then
        log_success "✓ Claude Code 安装验证通过"
    else
        log_warning "⚠ Claude Code 可能需要重新登录终端"
        # 不视为失败，因为可能需要重新登录
    fi
    
    return $success
}

# 显示使用说明
show_usage() {
    echo "使用方法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help      显示帮助信息"
    echo "  -c, --check     仅检查当前配置，不进行安装"
    echo "  -i, --install   完整安装和配置"
    echo "  -n, --node-only 仅安装Node.js和npm"
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
            -n|--node-only)
                mode="node-only"
                shift
                ;;
            *)
                log_error "未知选项: $1"
                ;;
        esac
    done
    
    echo -e "${GREEN}=== Claude+GLM配置脚本 for Linux Mint ===${NC}"
    echo
    
    check_root
    detect_system
    echo
    
    case "$mode" in
        "check")
            log_info "=== 检查模式 ==="
            is_node_installed
            check_git_installed
            if command -v claude &> /dev/null; then
                log_info "Claude Code: 已安装 ($(claude --version 2>/dev/null || echo '未知版本'))"
            else
                log_info "Claude Code: 未安装"
            fi
            ;;
            
        "node-only")
            log_info "=== 仅安装Node.js模式 ==="
            if ! is_node_installed; then
                install_node
            fi
            ;;
            
        "install")
            log_info "=== 完整安装模式 ==="
            
            # 安装Node.js（如果未安装）
            if ! is_node_installed; then
                install_node
            fi
            
            # 安装Git（如果未安装）
            if ! check_git_installed; then
                install_git
            fi
            
            # 安装Claude Code
            install_claude_code
            
            # 配置GLM环境
            configure_glm_env
            
            # 创建配置文件
            create_claude_config
            
            # 显示引导信息
            guide_glm_coding_plan
            
            # 验证安装
            verify_installation
            ;;
    esac
    
    echo
    log_success "配置完成!"
    echo "下一步操作:"
    echo "  1. 重新启动终端或运行: source ~/.bashrc"
    echo "  2. 在项目目录中运行: claude"
    echo "  3. 按照提示完成API Key配置"
    echo "  4. 开始使用Claude Code进行开发"
    echo
    echo "支持的功能:"
    echo "  - 对话/规划/代码编写/复杂推理 (GLM-4.6)"
    echo "  - 轻量任务自动路由 (GLM-4.5-Air)"
    echo "  - 视觉和搜索MCP服务器（需额外配置）"
}

# 执行主函数
main "$@"