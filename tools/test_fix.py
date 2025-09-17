#!/usr/bin/env python3
"""测试修复后的搜索逻辑"""

import sys
import os
sys.path.insert(0, '.')

from utils.logger import setup_logger
import yaml
from crawlers.arxiv_crawler import ArxivCrawler

def test_multiple_search_terms():
    print("🚀 测试修复后的搜索逻辑")
    print("=" * 50)
    
    # 设置日志
    logger = setup_logger('test_fix', 'DEBUG')
    
    # 加载配置
    with open('config/sources.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    arxiv_config = config['data_sources']['arxiv']
    
    # 显示搜索词信息
    search_terms = arxiv_config['search_terms']
    print(f"📊 配置信息:")
    print(f"   - 搜索词总数: {len(search_terms)}")
    print(f"   - max_results: {arxiv_config['max_results']}")
    print(f"   - 前3个搜索词:")
    for i, term in enumerate(search_terms[:3], 1):
        print(f"     {i}. {term}")
    
    # 创建爬虫
    print(f"\n🔧 创建ArxivCrawler...")
    crawler = ArxivCrawler(arxiv_config)
    
    # 测试获取论文（限制15篇，预期会搜索多个关键词）
    print(f"\n🔍 测试get_recent_papers(days=5, total_limit=15)...")
    print(f"   预期行为: 应该搜索多个关键词直到获得15篇有效论文")
    
    papers = crawler.get_recent_papers(days=5, total_limit=15)
    
    print(f"\n✅ 测试完成!")
    print(f"📈 结果统计:")
    print(f"   - 最终获得论文数: {len(papers)}")
    print(f"   - 前5篇论文:")
    for i, paper in enumerate(papers[:5], 1):
        print(f"     {i}. {paper.title[:60]}...")
    
    if len(papers) < 15:
        print(f"\n⚠️  注意: 获得论文数 ({len(papers)}) 小于限制 (15)")
        print(f"    这可能是因为最近5天内的相关论文确实较少")
    
    return len(papers)

if __name__ == "__main__":
    try:
        result_count = test_multiple_search_terms()
        print(f"\n🎯 测试结果: 获得 {result_count} 篇论文")
    except Exception as e:
        import traceback
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()