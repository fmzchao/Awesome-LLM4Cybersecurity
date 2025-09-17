#!/usr/bin/env python3
"""
LLM4Cybersecurity 工具演示脚本
展示主要功能和使用方法
"""

import sys
import os
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_paper_classification():
    """演示论文分类功能"""
    print("🔍 演示论文分类功能")
    print("=" * 50)
    
    # 示例论文数据
    demo_papers = [
        {
            "title": "Large Language Models for Vulnerability Detection in Smart Contracts",
            "authors": ["Alice Smith", "Bob Johnson"],
            "abstract": "This paper presents a novel approach using large language models to automatically detect vulnerabilities in smart contracts. We fine-tune GPT-3.5 on a dataset of known vulnerable contracts and achieve 92% accuracy in identifying common vulnerability patterns.",
            "venue": "arXiv",
            "url": "https://arxiv.org/abs/2401.12345"
        },
        {
            "title": "Adversarial Attacks on Large Language Model-based Security Systems",
            "authors": ["Charlie Brown", "Diana Prince"],
            "abstract": "We investigate the robustness of LLM-based security systems against adversarial attacks. Our findings show that carefully crafted prompts can bypass security filters and lead to unintended behaviors in AI security tools.",
            "venue": "IEEE Security & Privacy",
            "url": "https://ieeexplore.ieee.org/document/12345"
        },
        {
            "title": "Automated Penetration Testing Using GPT-4 and Reinforcement Learning",
            "authors": ["Eve Wilson", "Frank Miller"],
            "abstract": "This research combines GPT-4 with reinforcement learning to create an automated penetration testing framework. The system can adaptively discover and exploit vulnerabilities in web applications.",
            "venue": "ACM CCS",
            "url": "https://dl.acm.org/doi/10.1145/3456789"
        }
    ]
    
    try:
        from processors.paper_processor import PaperProcessor
        from utils.logger import setup_logger
        
        # 设置日志
        logger = setup_logger("demo", "logs/demo.log")
        
        # 创建处理器
        processor = PaperProcessor()
        
        print(f"📄 处理 {len(demo_papers)} 篇示例论文:\n")
        
        for i, paper_data in enumerate(demo_papers, 1):
            print(f"论文 {i}: {paper_data['title'][:60]}...")
            
            # 创建论文对象
            from crawlers.base_crawler import Paper
            paper = Paper(
                title=paper_data['title'],
                authors=paper_data['authors'],
                abstract=paper_data['abstract'],
                venue=paper_data['venue'],
                url=paper_data['url'],
                publish_date=datetime.now()
            )
            
            # 模拟分类（不调用真实API）
            # 根据关键词进行简单分类
            title_lower = paper.title.lower()
            abstract_lower = paper.abstract.lower()
            
            if any(keyword in title_lower + abstract_lower for keyword in 
                   ['vulnerability', 'detection', 'smart contract', 'penetration testing']):
                category = "Vulnerabilities Detection"
                confidence = 0.85
            elif any(keyword in title_lower + abstract_lower for keyword in 
                     ['adversarial', 'attack', 'robustness', 'security']):
                category = "LLM Security"
                confidence = 0.80
            else:
                category = "General Application"
                confidence = 0.70
            
            print(f"   分类结果: {category}")
            print(f"   置信度: {confidence}")
            print(f"   作者: {', '.join(paper.authors[:2])}{'...' if len(paper.authors) > 2 else ''}")
            print()
    
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有模块都已正确安装")

def demo_config_loading():
    """演示配置文件加载"""
    print("⚙️ 演示配置文件加载")
    print("=" * 50)
    
    import yaml
    
    config_files = [
        "config/classification_prompts.yaml",
        "config/sources.yaml", 
        "config/llm_config.yaml"
    ]
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            print(f"✅ {config_file}")
            
            if 'classification_prompts.yaml' in config_file:
                categories = list(config.get('categories', {}).keys())
                print(f"   包含 {len(categories)} 个分类类别")
                
            elif 'sources.yaml' in config_file:
                sources = list(config.get('sources', {}).keys())
                print(f"   配置 {len(sources)} 个数据源")
                
            elif 'llm_config.yaml' in config_file:
                available_llms = [k for k in config.keys() if k not in ['default_classifier', 'classifier_priority', 'batch_processing', 'error_handling', 'quality_control']]
                print(f"   支持 {len(available_llms)} 个LLM提供商")
                
        except Exception as e:
            print(f"❌ {config_file}: {e}")
        
        print()

def demo_statistics():
    """展示工具统计信息"""
    print("📊 工具功能统计")
    print("=" * 50)
    
    # 统计代码行数
    code_stats = {
        "Python文件": 0,
        "配置文件": 0,
        "总代码行数": 0
    }
    
    # 扫描文件
    for root, dirs, files in os.walk("."):
        if "venv" in root or "__pycache__" in root or ".git" in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            if file.endswith('.py'):
                code_stats["Python文件"] += 1
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        code_stats["总代码行数"] += lines
                except:
                    pass
                    
            elif file.endswith(('.yaml', '.yml')):
                code_stats["配置文件"] += 1
    
    print("📁 文件统计:")
    for key, value in code_stats.items():
        print(f"   {key}: {value}")
    
    print("\n🎯 主要功能模块:")
    modules = [
        "arXiv论文爬取",
        "OpenAI智能分类",
        "README自动更新", 
        "缓存管理",
        "日志系统",
        "数据验证",
        "配置管理"
    ]
    
    for i, module in enumerate(modules, 1):
        print(f"   {i}. {module}")

def main():
    """主演示函数"""
    print("🎉 LLM4Cybersecurity 工具演示")
    print("=" * 60)
    print("这是一个为 Awesome-LLM4Cybersecurity 项目开发的")
    print("自动化文档更新工具的演示脚本。")
    print("=" * 60)
    print()
    
    # 检查环境
    print("🔍 环境检查:")
    print(f"   Python版本: {sys.version.split()[0]}")
    print(f"   工作目录: {os.getcwd()}")
    print(f"   系统平台: {sys.platform}")
    print()
    
    # 演示各功能
    demo_config_loading()
    demo_paper_classification()
    demo_statistics()
    
    print("🚀 演示完成！")
    print("\n📖 使用指南:")
    print("   1. 配置 API 密钥在 config/llm_config.yaml")
    print("   2. 运行 python main.py --dry-run 进行预览")
    print("   3. 运行 python main.py 正式更新文档")
    print("\n💡 更多信息请查看 README.md")

if __name__ == "__main__":
    main()