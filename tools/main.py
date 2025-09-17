#!/usr/bin/env python3
"""
LLM4Cybersecurity文档自动更新工具

该工具从多个学术数据源获取最新论文，使用大语言模型进行智能分类，
并自动更新README.md文件。
"""

import os
import sys
import yaml
import argparse
from datetime import datetime, timedelta
from typing import List, Dict
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawlers.arxiv_crawler import ArxivCrawler
from classifiers.openai_classifier import OpenAIClassifier
from processors.paper_processor import PaperProcessor
from processors.readme_updater import ReadmeUpdater
from utils.logger import setup_logger, get_default_log_file
from utils.cache import CacheManager
from utils.validators import DataValidator

def load_config(config_dir: str) -> Dict:
    """加载配置文件"""
    config = {}
    
    config_files = {
        'sources': 'sources.yaml',
        'classification_prompts': 'classification_prompts.yaml', 
        'llm_config': 'llm_config.yaml',
        'examples': 'classification_examples.yaml'
    }
    
    for key, filename in config_files.items():
        file_path = os.path.join(config_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                config[key] = yaml.safe_load(f)
        else:
            print(f"警告: 配置文件不存在: {file_path}")
    
    return config

def setup_environment():
    """设置环境变量"""
    # 从环境变量加载API密钥
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'IEEE_API_KEY': os.getenv('IEEE_API_KEY'),
        'CLAUDE_API_KEY': os.getenv('CLAUDE_API_KEY')
    }
    
    missing_keys = [key for key, value in api_keys.items() if not value]
    if 'OPENAI_API_KEY' in missing_keys:
        print("错误: 请设置OPENAI_API_KEY环境变量")
        print("示例: export OPENAI_API_KEY='your-api-key'")
        return False
    
    if missing_keys:
        print(f"注意: 以下API密钥未设置: {', '.join(missing_keys)}")
        print("某些数据源可能无法使用")
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="LLM4Cybersecurity文档自动更新工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py                          # 获取最近7天的论文
  python main.py --days 3                 # 获取最近3天的论文
  python main.py --sources arxiv          # 仅从arXiv获取
  python main.py --dry-run               # 预览模式，不实际更新
  python main.py --config ./my_config/   # 使用自定义配置
        """
    )
    
    parser.add_argument('--config', default='config/',
                       help='配置文件目录 (默认: config/)')
    parser.add_argument('--sources', nargs='+', 
                       choices=['arxiv', 'acm', 'ieee'],
                       help='指定数据源 (默认: 所有可用源)')
    parser.add_argument('--days', type=int, default=7,
                       help='获取最近N天的论文 (默认: 7)')
    parser.add_argument('--max-papers', type=int, default=100,
                       help='每个数据源最大论文数 (默认: 100)')
    parser.add_argument('--dry-run', action='store_true',
                       help='预览模式，显示结果但不更新文件')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='日志级别 (默认: INFO)')
    parser.add_argument('--readme-path', default='../README.md',
                       help='README文件路径 (默认: ../README.md)')
    parser.add_argument('--clear-cache', action='store_true',
                       help='清空缓存后再运行')
    
    args = parser.parse_args()
    
    # 检查环境
    if not setup_environment():
        sys.exit(1)
    
    # 设置日志
    log_file = get_default_log_file()
    logger = setup_logger(level=args.log_level, log_file=log_file)
    
    logger.info("=" * 60)
    logger.info("LLM4Cybersecurity文档自动更新工具启动")
    logger.info(f"运行参数: days={args.days}, sources={args.sources}, dry_run={args.dry_run}")
    
    try:
        # 加载配置
        logger.info("加载配置文件...")
        config = load_config(args.config)
        
        if not config:
            logger.error("配置文件加载失败")
            sys.exit(1)
        
        # 验证配置
        validator = DataValidator()
        if not validator.validate_config(config):
            logger.error("配置文件验证失败")
            sys.exit(1)
        
        # 初始化缓存管理器
        cache_manager = CacheManager()
        if args.clear_cache:
            logger.info("清空缓存...")
            cache_manager.clear_all_cache()
        else:
            cache_manager.clean_expired_cache()
        
        # 初始化组件
        logger.info("初始化组件...")
        
        # 分类器
        llm_config = config['llm_config']['openai']
        llm_config['api_key'] = os.getenv('OPENAI_API_KEY')
        classifier = OpenAIClassifier(
            llm_config, 
            os.path.join(args.config, 'classification_prompts.yaml')
        )
        
        # 处理器
        processor = PaperProcessor()
        
        # README更新器
        if not os.path.exists(args.readme_path):
            logger.error(f"README文件不存在: {args.readme_path}")
            sys.exit(1)
        
        updater = ReadmeUpdater(args.readme_path)
        if not updater.validate_readme_structure():
            logger.warning("README文件结构可能存在问题")
        
        # 初始化爬虫
        crawlers = {}
        sources_to_use = args.sources or ['arxiv']  # 暂时只支持arxiv
        
        for source in sources_to_use:
            if source == 'arxiv' and 'sources' in config:
                arxiv_config = config['sources']['data_sources'].get('arxiv', {})
                crawlers[source] = ArxivCrawler(arxiv_config)
                logger.info(f"初始化 {source} 爬虫")
            else:
                logger.warning(f"数据源 {source} 暂不支持或配置缺失")
        
        if not crawlers:
            logger.error("没有可用的数据源")
            sys.exit(1)
        
        # 获取论文
        logger.info(f"开始获取最近 {args.days} 天的论文...")
        all_papers = []
        cutoff_date = datetime.now() - timedelta(days=args.days)
        
        for source, crawler in crawlers.items():
            logger.info(f"从 {source} 获取论文...")
            
            if source == 'arxiv':
                try:
                    # 获取最近论文
                    recent_papers = crawler.get_recent_papers(args.days)
                    
                    # 过滤已处理的论文
                    new_papers = []
                    for paper in recent_papers:
                        if not cache_manager.is_paper_processed(paper.url, paper.title):
                            if not cache_manager.is_paper_failed(paper.url, paper.title):
                                new_papers.append(paper)
                    
                    logger.info(f"从 {source} 获取到 {len(recent_papers)} 篇论文，其中 {len(new_papers)} 篇为新论文")
                    all_papers.extend(new_papers)
                    
                except Exception as e:
                    logger.error(f"从 {source} 获取论文失败: {e}")
                    continue
            
            # 避免请求过于频繁
            time.sleep(1)
        
        logger.info(f"总共获取到 {len(all_papers)} 篇新论文")
        
        if not all_papers:
            logger.info("没有找到新论文，程序结束")
            return
        
        # 验证论文数据
        logger.info("验证论文数据...")
        valid_papers = []
        for paper in all_papers:
            if validator.validate_paper(paper):
                valid_papers.append(paper)
            else:
                cache_manager.mark_paper_failed(paper.url, paper.title, "数据验证失败")
        
        logger.info(f"数据验证通过: {len(valid_papers)} 篇论文")
        
        if not valid_papers:
            logger.info("没有有效的论文数据，程序结束")
            return
        
        # 分类论文
        logger.info("开始分类论文...")
        categories_config = config['classification_prompts']['categories']
        
        classified_papers = {}
        classification_stats = {'success': 0, 'failed': 0, 'total': len(valid_papers)}
        
        for i, paper in enumerate(valid_papers, 1):
            logger.info(f"分类论文 {i}/{len(valid_papers)}: {paper.title[:50]}...")
            
            try:
                classification = classifier.classify_paper(paper, categories_config)
                processed_paper = processor.process_paper(paper, classification)
                
                # 验证处理后的论文
                if validator.validate_processed_paper(processed_paper):
                    category_key = f"{classification.category}_{classification.subcategory}"
                    if category_key not in classified_papers:
                        classified_papers[category_key] = []
                    classified_papers[category_key].append(processed_paper)
                    
                    # 标记为已处理
                    cache_manager.mark_paper_processed(
                        paper.url, paper.title, 
                        classification.subcategory, classification.confidence
                    )
                    
                    classification_stats['success'] += 1
                    logger.info(f"  -> 分类为: {classification.subcategory} (置信度: {classification.confidence:.2f})")
                else:
                    cache_manager.mark_paper_failed(paper.url, paper.title, "处理后验证失败")
                    classification_stats['failed'] += 1
                
            except Exception as e:
                logger.error(f"论文分类失败: {paper.title[:50]}... - {e}")
                cache_manager.mark_paper_failed(paper.url, paper.title, str(e))
                classification_stats['failed'] += 1
                continue
            
            # 避免API调用过于频繁
            time.sleep(0.5)
        
        logger.info(f"分类完成: 成功 {classification_stats['success']}, 失败 {classification_stats['failed']}")
        
        if not classified_papers:
            logger.info("没有成功分类的论文，程序结束")
            return
        
        # 去重处理
        all_processed_papers = []
        for papers in classified_papers.values():
            all_processed_papers.extend(papers)
        
        unique_papers = validator.check_duplicate_papers(all_processed_papers)
        
        # 重新按分类分组
        final_classified_papers = {}
        for paper in unique_papers:
            category_key = f"{paper.category}_{paper.subcategory}"
            if category_key not in final_classified_papers:
                final_classified_papers[category_key] = []
            final_classified_papers[category_key].append(paper)
        
        # 显示预览
        if args.dry_run or logger.level <= 20:  # INFO级别
            preview = updater.preview_changes(final_classified_papers)
            print("\n" + preview + "\n")
        
        # 更新README
        if not args.dry_run:
            logger.info("开始更新README文件...")
            
            # 创建备份
            backup_path = updater.backup_readme()
            if backup_path:
                logger.info(f"README备份已创建: {backup_path}")
            
            # 更新各分类
            total_added = 0
            for category_key, papers in final_classified_papers.items():
                if papers:
                    category, subcategory = category_key.split('_', 1)
                    success = updater.add_papers_to_category(papers, category, subcategory)
                    if success:
                        total_added += len(papers)
                        logger.info(f"成功添加 {len(papers)} 篇论文到 {subcategory}")
                    else:
                        logger.error(f"添加论文到 {subcategory} 失败")
            
            # 更新统计信息
            if total_added > 0:
                current_counts = updater.count_existing_papers()
                total_papers = current_counts.get('total', 0)
                
                updater.update_statistics(total_added, total_papers)
                logger.info(f"已更新统计信息: 新增 {total_added} 篇论文，总计 {total_papers} 篇")
            
            logger.info("README文件更新完成")
        else:
            logger.info("预览模式，未实际更新文件")
        
        # 生成统计报告
        stats = processor.generate_statistics(unique_papers)
        cache_stats = cache_manager.get_cache_stats()
        
        logger.info("=" * 40 + " 运行统计 " + "=" * 40)
        logger.info(f"总论文数: {stats['total_papers']}")
        logger.info(f"平均置信度: {stats['average_confidence']:.2f}")
        logger.info(f"高置信度论文: {stats['confidence_distribution']['high']}")
        logger.info(f"中置信度论文: {stats['confidence_distribution']['medium']}")
        logger.info(f"低置信度论文: {stats['confidence_distribution']['low']}")
        logger.info(f"缓存统计: 已处理 {cache_stats['processed_papers']} 篇，失败 {cache_stats['failed_papers']} 篇")
        logger.info("=" * 90)
        
        logger.info("程序执行完成")
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()