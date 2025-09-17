#!/bin/bash

# LLM4Cybersecurity 文档更新工具 - 快速开始脚本

echo "🚀 LLM4Cybersecurity 文档更新工具"
echo "=================================="

# 检查是否在正确的目录
if [ ! -f "main.py" ]; then
    echo "❌ 错误: 请在 tools 目录下运行此脚本"
    exit 1
fi

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到 Python，请先安装 Python"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 虚拟环境创建失败"
        exit 1
    fi
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt -q

# 检查配置文件
if [ ! -f "config/llm_config.yaml" ]; then
    echo "❌ 错误: 未找到 config/llm_config.yaml"
    echo "💡 请复制 config/llm_config.yaml.example 并填入你的API密钥"
    exit 1
fi

# 运行测试
echo "🧪 运行测试..."
python test_tool.py

if [ $? -eq 0 ]; then
    echo "✅ 测试通过！"
    echo ""
    echo "🎯 现在你可以运行以下命令："
    echo "   python main.py --dry-run     # 预览模式"
    echo "   python main.py --days 3      # 获取最近3天的论文"
    echo "   python main.py               # 正式运行"
    echo ""
    echo "📖 更多用法请查看 README.md"
else
    echo "❌ 测试失败，请检查配置"
    exit 1
fi