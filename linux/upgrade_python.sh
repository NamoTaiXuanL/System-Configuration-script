#!/bin/bash

# Python升级脚本 for Linux Mint 22.2
# 功能：检测当前Python版本并安装Python 3.13

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
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行，请使用sudo执行"
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

# 检测当前Python版本
detect_python_versions() {
    log_info "检测当前Python版本..."
    
    echo "系统Python版本:"
    if command -v python3 &> /dev/null; then
        python3 --version | awk '{print "  " $0}'
    else
        echo "  Python3 未安装"
    fi
    
    if command -v python &> /dev/null; then
        python --version | awk '{print "  " $0}'
    fi
    
    # 检查是否有其他Python版本
    echo "其他Python版本:"
    ls /usr/bin/python* 2>/dev/null | grep -E 'python[0-9]\.[0-9]+$' | while read -r py; do
        $py --version 2>&1 | awk '{print "  " $0}'
    done
}

# 安装依赖包
install_dependencies() {
    log_info "安装编译Python 3.13所需的依赖包..."
    
    apt update
    apt install -y \
        build-essential \
        zlib1g-dev \
        libncurses5-dev \
        libgdbm-dev \
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libffi-dev \
        libsqlite3-dev \
        libbz2-dev \
        wget \
        curl \
        git
}

# 下载Python 3.13源码
download_python_source() {
    local version="3.13.0"
    local url="https://www.python.org/ftp/python/$version/Python-$version.tgz"
    local temp_dir="/tmp/python_install"
    local script_dir="$(dirname "$(realpath "$0")")"
    local local_package="$script_dir/Python-$version.tgz"
    
    log_info "创建临时目录: $temp_dir"
    mkdir -p "$temp_dir"
    cd "$temp_dir"
    
    # 首先检查脚本所在目录的package子目录是否有本地包
    local package_dir="$script_dir/package"
    local package_in_dir="$package_dir/Python-$version.tgz"

    if [[ -f "$package_in_dir" ]]; then
        log_info "发现本地Python安装包: $package_in_dir"
        log_info "使用本地包进行安装..."
        cp "$package_in_dir" .
        log_success "本地包复制完成"
    elif [[ -f "$local_package" ]]; then
        log_info "发现本地Python安装包: $local_package"
        log_info "使用本地包进行安装..."
        cp "$local_package" .
        log_success "本地包复制完成"
    else
        log_info "未找到本地Python安装包，开始下载Python $version 源码..."
        if wget "$url"; then
            log_success "下载完成"
        else
            log_error "下载失败，请检查网络连接"
        fi
    fi
    
    log_info "解压源码包..."
    tar -xzf "Python-$version.tgz"
    cd "Python-$version"
}

# 编译安装Python 3.13
compile_install_python() {
    log_info "配置编译选项..."
    
    ./configure \
        --enable-optimizations \
        --enable-shared \
        --prefix=/usr/local \
        LDFLAGS="-Wl,-rpath=/usr/local/lib"
    
    log_info "开始编译Python 3.13 (这可能需要一些时间)..."
    make -j$(nproc)
    
    log_info "安装Python 3.13..."
    make altinstall
    
    # 创建符号链接
    if [[ ! -f /usr/local/bin/python3.13 ]]; then
        ln -sf /usr/local/bin/python3.13 /usr/local/bin/python3
    fi
}

# 验证安装
verify_installation() {
    log_info "验证Python 3.13安装..."
    
    if /usr/local/bin/python3.13 --version; then
        log_success "Python 3.13 安装成功!"
        
        # 显示安装位置
        echo "安装位置: /usr/local/bin/python3.13"
        echo "符号链接: /usr/local/bin/python3"
        
        # 测试基本功能
        echo "测试Python功能:"
        /usr/local/bin/python3.13 -c "print('Hello from Python 3.13!')"
        
    else
        log_error "Python 3.13 安装失败"
    fi
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."
    rm -rf /tmp/python_install
}

# 显示使用说明
show_usage() {
    echo "使用方法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -c, --check    仅检查Python版本，不安装"
    echo "  -i, --install  安装Python 3.13"
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
            *)
                log_error "未知选项: $1"
                ;;
        esac
    done
    
    echo -e "${GREEN}=== Python版本检测和升级脚本 ===${NC}"
    echo
    
    detect_system
    echo
    
    detect_python_versions
    echo
    
    if [[ "$mode" == "check" ]]; then
        log_info "仅检查模式，不进行安装"
        exit 0
    fi
    
    # 确认安装
    echo "此操作将:"
    echo "  1. 安装编译依赖包"
    echo "  2. 下载Python 3.13源码"
    echo "  3. 编译并安装Python 3.13到/usr/local"
    echo "  4. 创建符号链接"
    echo
    read -p "是否继续安装Python 3.13？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "用户取消安装"
        exit 0
    fi
    
    check_root
    install_dependencies
    download_python_source
    compile_install_python
    verify_installation
    cleanup
    
    echo
    log_success "Python 3.13 安装完成!"
    echo "您现在可以使用以下命令来使用Python 3.13:"
    echo "  /usr/local/bin/python3.13"
    echo "  /usr/local/bin/python3"
    echo
    echo "注意: 系统自带的Python版本仍然保留，不会受到影响"
}

# 执行主函数
main "$@"