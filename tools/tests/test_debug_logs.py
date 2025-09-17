#!/usr/bin/env python3
"""
调试日志功能测试脚本
演示增强的调试日志输出
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger
from crawlers.arxiv_crawler import ArxivCrawler

def test_debug_logging():
    """测试调试日志功能"""
    print("🚀 测试调试日志功能")
    print("=" * 60)
    
    # 设置DEBUG级别日志
    logger = setup_logger("debug_test", "DEBUG", "logs/debug_test.log")
    
    print("📝 设置DEBUG级别日志记录器...")
    print("🔍 以下是调试日志的输出示例:")
    print("-" * 60)
    
    # 模拟配置
    config = {
        'base_url': 'http://export.arxiv.org/api/query',
        'search_terms': [
            'cybersecurity AND (large language model OR LLM OR GPT)',
            'vulnerability detection AND machine learning'
        ],
        'max_results': 3,
        'enabled': True
    }
    
    # 创建arXiv爬虫
    logger.info("初始化arXiv爬虫...")
    logger.debug(f"爬虫配置: {config}")
    
    crawler = ArxivCrawler(config)
    
    # 模拟获取论文过程
    logger.info("开始获取最近1天的论文...")
    cutoff_date = datetime.now() - timedelta(days=1)
    logger.debug(f"搜索截止日期: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 模拟论文获取（实际会调用API）
        logger.debug("调用 get_recent_papers 方法...")
        
        # 为了演示，我们只显示日志结构，不实际调用API
        logger.debug("将使用 2 个搜索词，每个最多获取 3 篇论文")
        
        for i, query in enumerate(config['search_terms'], 1):
            logger.debug(f"正在搜索 {i}/{len(config['search_terms'])}: {query}")
            logger.debug(f"发送请求到: {config['base_url']}")
            logger.debug(f"请求参数: search_query='{query}', max_results=3")
            
            # 模拟响应
            logger.debug("收到响应，状态码: 200")
            logger.debug("响应内容长度: 15234 字符")
            logger.debug("开始解析XML响应...")
            logger.debug("XML解析完成，获得 5 篇论文")
            logger.debug("开始过滤网络安全相关论文...")
            
            # 模拟过滤结果
            for j in range(1, 4):  # 模拟3篇论文
                if j <= 2:
                    logger.debug(f"  ✅ 第{j}篇相关: Adversarial Attacks on Large Language Models for...")
                else:
                    logger.debug(f"  ❌ 第{j}篇不相关: Deep Learning Applications in Computer Vision...")
            
            logger.info(f"从arXiv获取到 5 篇论文，筛选出 2 篇网络安全相关论文")
            logger.debug(f"搜索词 '{query}' 获得 2 篇相关论文")
            
            if i < len(config['search_terms']):
                logger.debug("等待1秒避免请求过于频繁...")
        
        logger.debug("所有搜索词总共获得 4 篇论文")
        logger.debug("开始过滤日期并去重...")
        
        # 模拟去重过程
        logger.debug("  ✅ 保留论文: Large Language Models for Cybersecurity Threat... (发布于 2025-01-16)")
        logger.debug("  ✅ 保留论文: Automated Vulnerability Detection using GPT-4... (发布于 2025-01-16)")
        logger.debug("  跳过重复论文: Large Language Models for Cybersecurity Threat...")
        logger.debug("  跳过过旧论文: Machine Learning in Network Security... (发布于 2025-01-15)")
        
        logger.info("过滤结果: 保留 2 篇，过旧 1 篇，重复 1 篇")
        
        logger.info("论文获取阶段完成，准备进行数据验证...")
        
        # 模拟验证过程
        logger.info("验证论文数据...")
        for i in range(1, 3):
            logger.debug(f"验证论文 {i}/2: Large Language Models for Cybersecurity...")
            logger.debug("  ✅ 验证通过")
        
        logger.info("数据验证通过: 2 篇论文")
        logger.debug("验证统计 - 通过: 2, 失败: 0")
        
        # 模拟分类过程
        logger.info("开始分类论文...")
        logger.debug("加载分类配置: 29 个类别")
        
        for i in range(1, 3):
            logger.info(f"分类论文 {i}/2: Large Language Models for Cybersecurity...")
            logger.debug(f"  论文作者: John Smith, Alice Johnson, Bob Wilson...")
            logger.debug(f"  发布日期: 2025-01-16")
            logger.debug(f"  摘要长度: 1245 字符")
            logger.debug(f"  开始调用分类器...")
            logger.debug(f"  分类器返回结果: RQ1/Vulnerabilities Detection")
            logger.debug(f"  论文处理完成")
            logger.info(f"  -> 分类为: Vulnerabilities Detection (置信度: 0.85)")
            logger.debug(f"  -> 分类推理: The paper focuses on using large language models for automated vulnerability...")
            logger.debug(f"等待0.5秒避免API调用过于频繁...")
        
        logger.info("分类完成: 成功 2, 失败 0")
        
        print("-" * 60)
        print("✅ 调试日志演示完成！")
        print()
        print("💡 实际使用时，这些日志会帮助你:")
        print("   • 监控论文获取的实时状态")
        print("   • 了解每个搜索词的效果")
        print("   • 排查网络请求问题")
        print("   • 跟踪分类过程和结果")
        print("   • 分析缓存命中情况")
        print("   • 诊断API调用错误")
        
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        logger.debug(f"详细错误信息: {str(e)}", exc_info=True)

def show_log_levels():
    """展示不同日志级别的输出"""
    print("\n📊 不同日志级别的输出对比:")
    print("=" * 60)
    
    levels = ['INFO', 'DEBUG']
    
    for level in levels:
        print(f"\n🔍 {level} 级别日志:")
        print("-" * 30)
        
        logger = setup_logger(f"test_{level.lower()}", level, f"logs/test_{level.lower()}.log")
        
        logger.info("开始获取最近7天的论文...")
        logger.debug("搜索截止日期: 2025-01-10 15:30:45")
        logger.info("从 arxiv 获取论文...")
        logger.debug("使用爬虫配置: {'base_url': '...', 'max_results': 50}")
        logger.debug("开始调用 arxiv 爬虫获取论文...")
        logger.info("从 arxiv 获取到 15 篇论文，其中 8 篇为新论文")
        logger.debug("缓存统计 - 已处理: 5, 已失败: 2, 新论文: 8")
        logger.info("验证论文数据...")
        logger.debug("验证论文 1/8: Large Language Models for...")
        logger.debug("  ✅ 验证通过")
        logger.info("数据验证通过: 8 篇论文")
        
        print()

def main():
    print("🎯 LLM4Cybersecurity 调试日志功能测试")
    print("=" * 80)
    print("这个脚本演示了工具在DEBUG模式下的详细日志输出。")
    print("=" * 80)
    
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    
    # 测试调试日志
    test_debug_logging()
    
    # 展示不同日志级别
    show_log_levels()
    
    print("\n🚀 使用方法:")
    print("   在实际运行时，使用以下命令启用详细日志:")
    print("   python main.py --log-level DEBUG --dry-run")
    print()
    print("📁 日志文件位置:")
    print("   • 主日志: logs/app.log")
    print("   • 错误日志: logs/error.log")
    print("   • 调试日志: logs/debug.log")

if __name__ == "__main__":
    main()