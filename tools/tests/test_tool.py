#!/usr/bin/env python3
"""
快速测试脚本 - 验证工具组件是否正常工作
"""

import os
import sys
import yaml
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 修改导入方式，避免相对导入问题
        import sys
        import os
        
        # 确保当前目录在Python路径中
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 绝对导入
        from crawlers.base_crawler import Paper, BaseCrawler
        from crawlers.arxiv_crawler import ArxivCrawler
        from classifiers.base_classifier import ClassificationResult
        from classifiers.openai_classifier import OpenAIClassifier
        from processors.paper_processor import PaperProcessor, ProcessedPaper
        from processors.readme_updater import ReadmeUpdater
        from utils.logger import setup_logger
        from utils.cache import CacheManager
        from utils.validators import DataValidator
        
        print("✅ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config_loading():
    """测试配置文件加载"""
    print("\n🔍 测试配置文件加载...")
    
    config_files = [
        'config/sources.yaml',
        'config/classification_prompts.yaml', 
        'config/llm_config.yaml'
    ]
    
    for config_file in config_files:
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                print(f"✅ {config_file} 加载成功")
            else:
                print(f"⚠️  {config_file} 文件不存在")
                return False
        except Exception as e:
            print(f"❌ {config_file} 加载失败: {e}")
            return False
    
    return True

def test_paper_creation():
    """测试论文对象创建"""
    print("\n🔍 测试论文对象创建...")
    
    try:
        from crawlers.base_crawler import Paper
        
        # 创建测试论文
        test_paper = Paper(
            title="Test Paper: Large Language Models for Cybersecurity",
            authors=["John Doe", "Jane Smith"],
            abstract="This is a test abstract about LLMs and cybersecurity applications.",
            url="https://arxiv.org/abs/2401.12345",
            publish_date=datetime.now(),
            venue="arXiv",
            keywords=["cybersecurity", "LLM", "AI"]
        )
        
        print("✅ 论文对象创建成功")
        print(f"   标题: {test_paper.title}")
        print(f"   作者: {', '.join(test_paper.authors)}")
        print(f"   venue: {test_paper.venue}")
        
        return True, test_paper
    except Exception as e:
        print(f"❌ 论文对象创建失败: {e}")
        return False, None

def test_processor():
    """测试处理器"""
    print("\n🔍 测试论文处理器...")
    
    try:
        from processors.paper_processor import PaperProcessor
        from classifiers.base_classifier import ClassificationResult
        
        processor = PaperProcessor()
        
        # 创建测试分类结果
        classification = ClassificationResult(
            category="rq2",
            subcategory="Vulnerabilities Detection",
            confidence=0.85,
            reasoning="测试分类"
        )
        
        # 这里需要之前创建的测试论文
        success, test_paper = test_paper_creation()
        if not success or test_paper is None:
            return False
        
        processed_paper = processor.process_paper(test_paper, classification)
        
        print("✅ 论文处理成功")
        print(f"   分类: {processed_paper.subcategory}")
        print(f"   置信度: {processed_paper.confidence}")
        
        return True
    except Exception as e:
        print(f"❌ 论文处理失败: {e}")
        return False

def test_cache_manager():
    """测试缓存管理器"""
    print("\n🔍 测试缓存管理器...")
    
    try:
        from utils.cache import CacheManager
        
        cache = CacheManager("test_cache")
        
        # 测试基本功能
        test_url = "https://test.com/paper1"
        test_title = "Test Paper Title"
        
        # 检查未处理状态
        if not cache.is_paper_processed(test_url, test_title):
            print("✅ 初始状态检查正确")
        
        # 标记为已处理
        cache.mark_paper_processed(test_url, test_title, "test_category", 0.8)
        
        # 检查已处理状态  
        if cache.is_paper_processed(test_url, test_title):
            print("✅ 处理状态更新正确")
        
        # 获取统计信息
        stats = cache.get_cache_stats()
        print(f"✅ 缓存统计: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ 缓存管理器测试失败: {e}")
        return False

def test_validator():
    """测试数据验证器"""
    print("\n🔍 测试数据验证器...")
    
    try:
        from utils.validators import DataValidator
        
        validator = DataValidator()
        
        # 测试URL验证
        test_urls = [
            ("https://arxiv.org/abs/2401.12345", True),
            ("https://dl.acm.org/doi/10.1145/3456789", True),
            ("invalid-url", False),
            ("", False)
        ]
        
        for url, expected in test_urls:
            result = validator.validate_url(url)
            if result == expected:
                print(f"✅ URL验证正确: {url}")
            else:
                print(f"❌ URL验证错误: {url}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ 数据验证器测试失败: {e}")
        return False

def test_logger():
    """测试日志系统"""
    print("\n🔍 测试日志系统...")
    
    try:
        from utils.logger import setup_logger
        
        logger = setup_logger("test_logger", level="INFO", console_output=True)
        logger.info("这是一条测试日志信息")
        logger.warning("这是一条测试警告信息")
        
        print("✅ 日志系统正常工作")
        return True
    except Exception as e:
        print(f"❌ 日志系统测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行工具测试...\n")
    
    tests = [
        ("模块导入", test_imports),
        ("配置文件加载", test_config_loading),
        ("论文处理器", test_processor),
        ("缓存管理器", test_cache_manager),
        ("数据验证器", test_validator),
        ("日志系统", test_logger)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试出现异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果汇总
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！工具已准备就绪。")
        return True
    else:
        print("⚠️  部分测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)