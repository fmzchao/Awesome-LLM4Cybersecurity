#!/usr/bin/env python3
"""
诊断arXiv搜索问题的测试脚本
检查配置加载、搜索词使用和网络请求
"""

import sys
import os
import yaml
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger
from crawlers.arxiv_crawler import ArxivCrawler

def test_config_loading():
    """测试配置文件加载"""
    print("🔍 步骤1: 测试配置文件加载")
    print("=" * 50)
    
    try:
        # 加载sources配置
        with open('config/sources.yaml', 'r', encoding='utf-8') as f:
            sources_config = yaml.safe_load(f)
        
        print("✅ sources.yaml 加载成功")
        
        # 检查data_sources结构
        if 'data_sources' in sources_config:
            print(f"📊 发现data_sources配置")
            data_sources = sources_config['data_sources']
            
            # 检查arxiv配置
            if 'arxiv' in data_sources:
                arxiv_config = data_sources['arxiv']
                print(f"📊 arXiv配置信息:")
                print(f"   - enabled: {arxiv_config.get('enabled', 'N/A')}")
                print(f"   - base_url: {arxiv_config.get('base_url', 'N/A')}")
                print(f"   - max_results: {arxiv_config.get('max_results', 'N/A')}")
                
                # 检查搜索词
                if 'search_terms' in arxiv_config:
                    search_terms = arxiv_config['search_terms']
                    print(f"   - 搜索词数量: {len(search_terms)}")
                    print(f"📝 搜索词列表:")
                    for i, term in enumerate(search_terms, 1):
                        print(f"   {i:2d}. {term}")
                        if i == 5:  # 只显示前5个
                            print(f"   ... 还有 {len(search_terms) - 5} 个搜索词")
                            break
                else:
                    print("❌ 未找到search_terms配置")
                    return False
            else:
                print("❌ 未找到arxiv配置")
                return False
        else:
            print("❌ 未找到data_sources配置")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_crawler_initialization():
    """测试爬虫初始化"""
    print("\n🔍 步骤2: 测试爬虫初始化")
    print("=" * 50)
    
    try:
        # 设置调试日志
        logger = setup_logger("test_crawler", "DEBUG", "logs/test_arxiv.log")
        
        # 加载配置
        with open('config/sources.yaml', 'r', encoding='utf-8') as f:
            sources_config = yaml.safe_load(f)
        
        arxiv_config = sources_config['data_sources']['arxiv']
        print(f"📊 传入爬虫的配置:")
        print(f"   {json.dumps(arxiv_config, indent=2, ensure_ascii=False)}")
        
        # 创建爬虫实例
        crawler = ArxivCrawler(arxiv_config)
        
        print(f"✅ 爬虫初始化成功")
        print(f"📊 爬虫属性:")
        print(f"   - base_url: {crawler.base_url}")
        print(f"   - config: {crawler.config}")
        
        return crawler
        
    except Exception as e:
        print(f"❌ 爬虫初始化失败: {e}")
        return None

def test_search_terms_usage(crawler):
    """测试搜索词的使用"""
    print("\n🔍 步骤3: 测试搜索词使用")
    print("=" * 50)
    
    if not crawler:
        print("❌ 爬虫未初始化，跳过测试")
        return False
    
    try:
        # 检查配置中的搜索词
        search_terms = crawler.config.get('search_terms', [])
        max_results = crawler.config.get('max_results', 50)
        
        print(f"📊 爬虫配置中的搜索词:")
        print(f"   - 搜索词数量: {len(search_terms)}")
        print(f"   - 每次最大结果数: {max_results}")
        
        if not search_terms:
            print("❌ 搜索词列表为空")
            return False
        
        # 显示前几个搜索词
        print(f"📝 将要使用的搜索词:")
        for i, term in enumerate(search_terms[:3], 1):
            print(f"   {i}. {term}")
        
        # 测试单个搜索词（不实际发送请求）
        test_query = search_terms[0]
        print(f"\n🧪 测试搜索词: {test_query}")
        print(f"📊 这个搜索词应该产生以下请求:")
        print(f"   - URL: {crawler.base_url}")
        print(f"   - 参数: search_query='{test_query}', max_results={max_results}")
        
        return True
        
    except Exception as e:
        print(f"❌ 搜索词测试失败: {e}")
        return False

def test_actual_search(crawler, dry_run=True):
    """测试实际搜索（可选择是否真实发送请求）"""
    print(f"\n🔍 步骤4: 测试实际搜索 ({'预览模式' if dry_run else '真实请求'})")
    print("=" * 50)
    
    if not crawler:
        print("❌ 爬虫未初始化，跳过测试")
        return False
    
    try:
        search_terms = crawler.config.get('search_terms', [])
        if not search_terms:
            print("❌ 没有搜索词可用")
            return False
        
        if dry_run:
            print("🔄 预览模式：模拟请求发送过程")
            for i, query in enumerate(search_terms[:2], 1):  # 只测试前2个
                print(f"\n   📤 模拟请求 {i}:")
                print(f"      搜索词: {query}")
                print(f"      URL: {crawler.base_url}")
                print(f"      参数: search_query='{query}', max_results=3")
                print(f"      状态: 🟡 已准备发送（预览模式跳过）")
        else:
            print("🔄 真实模式：发送实际请求")
            # 只使用第一个搜索词进行测试
            test_query = search_terms[0]
            print(f"   📤 发送真实请求: {test_query}")
            
            # 设置小的结果数量以加快测试
            papers = crawler.search_papers(test_query, max_results=3)
            print(f"   📥 收到响应: {len(papers)} 篇论文")
            
            if papers:
                print(f"   📝 示例论文:")
                for i, paper in enumerate(papers[:2], 1):
                    print(f"      {i}. {paper.title[:60]}...")
            else:
                print(f"   ⚠️ 未找到相关论文")
        
        return True
        
    except Exception as e:
        print(f"❌ 搜索测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recent_papers_method(crawler, days=1):
    """测试get_recent_papers方法"""
    print(f"\n🔍 步骤5: 测试get_recent_papers方法")
    print("=" * 50)
    
    if not crawler:
        print("❌ 爬虫未初始化，跳过测试")
        return False
    
    try:
        print(f"🔄 调用get_recent_papers(days={days})...")
        
        # 检查方法是否会使用所有搜索词
        search_terms = crawler.config.get('search_terms', [])
        print(f"📊 预期行为:")
        print(f"   - 将遍历 {len(search_terms)} 个搜索词")
        print(f"   - 每个搜索词最多获取 {crawler.config.get('max_results', 50)} 篇论文")
        print(f"   - 过滤最近 {days} 天的论文")
        
        # 实际调用（使用较少的搜索词进行测试）
        print(f"\n🧪 执行测试调用...")
        
        # 临时修改配置，只使用前2个搜索词进行测试
        original_search_terms = crawler.config.get('search_terms', [])
        crawler.config['search_terms'] = original_search_terms[:2]  # 只用前2个
        crawler.config['max_results'] = 3  # 限制结果数量
        
        papers = crawler.get_recent_papers(days)
        
        # 恢复原配置
        crawler.config['search_terms'] = original_search_terms
        
        print(f"✅ 方法调用完成")
        print(f"📊 结果:")
        print(f"   - 获得论文数量: {len(papers)}")
        
        if papers:
            print(f"📝 示例论文:")
            for i, paper in enumerate(papers[:3], 1):
                print(f"   {i}. {paper.title[:60]}...")
                print(f"      发布日期: {paper.publish_date.strftime('%Y-%m-%d')}")
                print(f"      URL: {paper.url}")
        else:
            print(f"⚠️ 未获得任何论文")
            print(f"💡 可能原因:")
            print(f"   - 最近{days}天内没有相关论文")
            print(f"   - 搜索词过于严格")
            print(f"   - 网络连接问题")
            print(f"   - arXiv API限制")
        
        return True
        
    except Exception as e:
        print(f"❌ get_recent_papers测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎯 arXiv搜索问题诊断工具")
    print("=" * 80)
    print("这个脚本将帮助诊断为什么搜索词没有被找到以及请求没有发送的问题")
    print("=" * 80)
    
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    
    # 步骤1: 测试配置加载
    config_ok = test_config_loading()
    
    if not config_ok:
        print("\n❌ 配置加载失败，无法继续测试")
        return 1
    
    # 步骤2: 测试爬虫初始化
    crawler = test_crawler_initialization()
    
    if not crawler:
        print("\n❌ 爬虫初始化失败，无法继续测试")
        return 1
    
    # 步骤3: 测试搜索词使用
    search_ok = test_search_terms_usage(crawler)
    
    if not search_ok:
        print("\n❌ 搜索词配置有问题")
        return 1
    
    # 步骤4: 测试搜索（预览模式）
    search_test_ok = test_actual_search(crawler, dry_run=True)
    
    # 步骤5: 询问是否进行真实请求测试
    print(f"\n❓ 是否要进行真实的网络请求测试？")
    print(f"   这将实际向arXiv发送请求（数量有限）")
    response = input("   输入 'y' 继续，其他任意键跳过: ").lower().strip()
    
    if response == 'y':
        test_actual_search(crawler, dry_run=False)
        test_recent_papers_method(crawler, days=1)
    else:
        print("⏭️ 跳过真实请求测试")
    
    print("\n" + "=" * 80)
    print("🔍 诊断总结:")
    print(f"   1. 配置加载: {'✅ 成功' if config_ok else '❌ 失败'}")
    print(f"   2. 爬虫初始化: {'✅ 成功' if crawler else '❌ 失败'}")
    print(f"   3. 搜索词配置: {'✅ 正常' if search_ok else '❌ 异常'}")
    print(f"   4. 搜索流程: {'✅ 正常' if search_test_ok else '❌ 异常'}")
    
    if config_ok and crawler and search_ok and search_test_ok:
        print("\n💡 建议:")
        print("   配置和代码看起来都正常。如果仍然没有找到论文，可能是因为:")
        print("   • 最近几天确实没有符合条件的新论文")
        print("   • 搜索词过于严格，建议尝试更宽泛的关键词")
        print("   • 网络连接问题或arXiv服务暂时不可用")
        print("   • 尝试增加天数参数: --days 7")
    else:
        print("\n❌ 发现问题，请检查上述失败的步骤")
    
    print("=" * 80)
    return 0

if __name__ == "__main__":
    sys.exit(main())