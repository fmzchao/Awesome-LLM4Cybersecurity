#!/bin/bash

# LLM4Cybersecurity 文档更新工具启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数定义
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装Python3"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Python版本过低，需要Python 3.8+，当前版本: $python_version"
        exit 1
    fi
    
    print_success "Python检查通过: $python_version"
}

# 检查依赖包
check_dependencies() {
    print_info "检查依赖包..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt 文件不存在"
        exit 1
    fi
    
    # 检查关键依赖
    missing_packages=()
    
    if ! python3 -c "import requests" 2>/dev/null; then
        missing_packages+=("requests")
    fi
    
    if ! python3 -c "import yaml" 2>/dev/null; then
        missing_packages+=("PyYAML")
    fi
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        print_warning "发现缺失的依赖包: ${missing_packages[*]}"
        print_info "正在安装依赖包..."
        pip3 install -r requirements.txt
        print_success "依赖包安装完成"
    else
        print_success "依赖包检查通过"
    fi
}

# 检查环境变量
check_environment() {
    print_info "检查环境变量..."
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY 环境变量未设置"
        print_info "请设置: export OPENAI_API_KEY='your-api-key'"
        exit 1
    fi
    
    print_success "环境变量检查通过"
    
    if [ -z "$IEEE_API_KEY" ]; then
        print_warning "IEEE_API_KEY 未设置，IEEE数据源将不可用"
    fi
}

# 检查配置文件
check_config() {
    print_info "检查配置文件..."
    
    config_files=(
        "config/sources.yaml"
        "config/classification_prompts.yaml"
        "config/llm_config.yaml"
    )
    
    for file in "${config_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "配置文件不存在: $file"
            exit 1
        fi
    done
    
    print_success "配置文件检查通过"
}

# 检查README文件
check_readme() {
    readme_path="../README.md"
    if [ ! -f "$readme_path" ]; then
        print_error "README.md 文件不存在: $readme_path"
        print_info "请确保在项目根目录运行此脚本"
        exit 1
    fi
    
    print_success "README文件检查通过"
}

# 创建必要目录
create_directories() {
    print_info "创建必要目录..."
    
    directories=(
        "logs"
        "data/cache"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_info "创建目录: $dir"
        fi
    done
    
    print_success "目录检查完成"
}

# 显示使用帮助
show_help() {
    echo -e "${BLUE}LLM4Cybersecurity 文档更新工具${NC}"
    echo ""
    echo "用法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h          显示此帮助信息"
    echo "  --install           仅安装依赖，不运行更新"
    echo "  --check             仅检查环境，不运行更新"
    echo "  --days N            获取最近N天的论文 (默认: 7)"
    echo "  --dry-run           预览模式，不实际更新文件"
    echo "  --sources LIST      指定数据源 (arxiv, acm, ieee)"
    echo "  --log-level LEVEL   日志级别 (DEBUG, INFO, WARNING, ERROR)"
    echo "  --clear-cache       清空缓存后运行"
    echo ""
    echo "示例:"
    echo "  $0                  # 标准运行，获取最近7天论文"
    echo "  $0 --days 3         # 获取最近3天论文"
    echo "  $0 --dry-run        # 预览模式"
    echo "  $0 --sources arxiv  # 仅使用arXiv数据源"
    echo "  $0 --clear-cache    # 清空缓存后运行"
}

# 运行工具
run_tool() {
    print_info "启动文档更新工具..."
    
    # 构建python命令
    cmd="python3 main.py"
    
    # 添加参数
    for arg in "$@"; do
        cmd="$cmd $arg"
    done
    
    print_info "执行命令: $cmd"
    eval $cmd
    
    if [ $? -eq 0 ]; then
        print_success "文档更新完成"
    else
        print_error "文档更新失败"
        exit 1
    fi
}

# 主函数
main() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "  LLM4Cybersecurity 文档更新工具"
    echo "=========================================="
    echo -e "${NC}"
    
    # 解析命令行参数
    install_only=false
    check_only=false
    tool_args=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --install)
                install_only=true
                shift
                ;;
            --check)
                check_only=true
                shift
                ;;
            *)
                tool_args+=("$1")
                shift
                ;;
        esac
    done
    
    # 执行检查
    check_python
    check_dependencies
    check_environment
    check_config
    check_readme
    create_directories
    
    if [ "$install_only" = true ]; then
        print_success "安装完成"
        exit 0
    fi
    
    if [ "$check_only" = true ]; then
        print_success "环境检查完成"
        exit 0
    fi
    
    # 运行工具
    run_tool "${tool_args[@]}"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi