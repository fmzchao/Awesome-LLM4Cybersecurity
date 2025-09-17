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

def setup_environment(dry_run: bool = False):
    """设置环境变量"""
    # 从环境变量加载API密钥
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'IEEE_API_KEY': os.getenv('IEEE_API_KEY'),
        'CLAUDE_API_KEY': os.getenv('CLAUDE_API_KEY')
    }
    
    missing_keys = [key for key, value in api_keys.items() if not value]
    
    # 在干运行模式下，允许没有OpenAI API密钥，只运行爬虫部分
    if 'OPENAI_API_KEY' in missing_keys and not dry_run:
        print("错误: 请设置OPENAI_API_KEY环境变量")
        print("示例: export OPENAI_API_KEY='your-api-key'")
        return False
    
    if missing_keys:
        print(f"注意: 以下API密钥未设置: {', '.join(missing_keys)}")
        if dry_run:
            print("干运行模式: 将跳过需要API密钥的操作")
        else:
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
    parser.add_argument('--readme-zh-path', default='../README_zh.md',
                       help='中文README文件路径 (默认: ../README_zh.md)')
    parser.add_argument('--update-zh', action='store_true', default=True,
                       help='是否同时更新中文README (默认: 开启)')
    parser.add_argument('--clear-cache', action='store_true',
                       help='清空缓存后再运行')
    
    args = parser.parse_args()
    
    # 检查环境
    if not setup_environment(args.dry_run):
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
        
        # 分类器（干运行模式下可以跳过）
        classifier = None
        if not args.dry_run or os.getenv('OPENAI_API_KEY'):
            llm_config = config['llm_config']['openai']
            llm_config['api_key'] = os.getenv('OPENAI_API_KEY')
            classifier = OpenAIClassifier(
                llm_config, 
                os.path.join(args.config, 'classification_prompts.yaml')
            )
        else:
            logger.warning("干运行模式且缺少API密钥，跳过分类器初始化")
        
        # 处理器
        processor = PaperProcessor()
        
        # README更新器
        updaters = []
        
        # 英文README更新器
        if not os.path.exists(args.readme_path):
            logger.error(f"README文件不存在: {args.readme_path}")
            sys.exit(1)
        
        en_updater = ReadmeUpdater(args.readme_path, language="en")
        if not en_updater.validate_readme_structure():
            logger.warning("英文README文件结构可能存在问题")
        updaters.append(("en", en_updater))
        
        # 中文README更新器（如果启用）
        if args.update_zh:
            if not os.path.exists(args.readme_zh_path):
                logger.warning(f"中文README文件不存在: {args.readme_zh_path}，跳过中文更新")
            else:
                zh_updater = ReadmeUpdater(args.readme_zh_path, language="zh")
                if not zh_updater.validate_readme_structure():
                    logger.warning("中文README文件结构可能存在问题")
                updaters.append(("zh", zh_updater))
                logger.info("将同时更新英文和中文README文件")
        
        logger.info(f"初始化了 {len(updaters)} 个README更新器")
        
        # 初始化爬虫
        crawlers = {}
        sources_to_use = args.sources or ['arxiv']  # 暂时只支持arxiv
        
        for source in sources_to_use:
            if source == 'arxiv' and 'sources' in config:
                arxiv_config = config['sources']['data_sources'].get('arxiv', {})
                # 将命令行参数覆盖配置文件中的值
                if args.max_papers is not None:
                    arxiv_config['max_results'] = args.max_papers
                    logger.debug(f"使用命令行指定的max_papers: {args.max_papers}")
                else:
                    logger.debug(f"使用配置文件中的max_results: {arxiv_config.get('max_results', 50)}")
                crawlers[source] = ArxivCrawler(arxiv_config)
                logger.info(f"初始化 {source} 爬虫")
            else:
                logger.warning(f"数据源 {source} 暂不支持或配置缺失")
        
        if not crawlers:
            logger.error("没有可用的数据源")
            sys.exit(1)
        
        # 获取论文
        logger.info(f"开始获取最近 {args.days} 天的论文...")
        cutoff_date = datetime.now() - timedelta(days=args.days)
        logger.debug(f"搜索截止日期: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        all_papers = []
        cutoff_date = datetime.now() - timedelta(days=args.days)
        
        for source, crawler in crawlers.items():
            logger.info(f"从 {source} 获取论文...")
            logger.debug(f"使用爬虫配置: {crawler.config}")
            
            if source == 'arxiv':
                try:
                    # 获取最近论文，传递总数限制参数
                    logger.debug(f"开始调用 {source} 爬虫获取论文...")
                    recent_papers = crawler.get_recent_papers(args.days, total_limit=args.max_papers)
                    logger.debug(f"从 {source} 原始获取论文数量: {len(recent_papers)}")
                    
                    # 过滤已处理的论文
                    new_papers = []
                    processed_count = 0
                    failed_count = 0
                    
                    for paper in recent_papers:
                        if cache_manager.is_paper_processed(paper.url, paper.title):
                            processed_count += 1
                            logger.debug(f"跳过已处理论文: {paper.title[:50]}...")
                        elif cache_manager.is_paper_failed(paper.url, paper.title):
                            failed_count += 1
                            logger.debug(f"跳过失败论文: {paper.title[:50]}...")
                        else:
                            new_papers.append(paper)
                            logger.debug(f"新论文待处理: {paper.title[:50]}...")
                    
                    logger.info(f"从 {source} 获取到 {len(recent_papers)} 篇论文，其中 {len(new_papers)} 篇为新论文")
                    logger.debug(f"缓存统计 - 已处理: {processed_count}, 已失败: {failed_count}, 新论文: {len(new_papers)}")
                    all_papers.extend(new_papers)
                    
                except Exception as e:
                    logger.error(f"从 {source} 获取论文失败: {e}")
                    logger.debug(f"详细错误信息: {str(e)}", exc_info=True)
                    continue
            
            # 避免请求过于频繁
            logger.debug(f"等待1秒避免请求过于频繁...")
            time.sleep(1)
        
        logger.info(f"总共获取到 {len(all_papers)} 篇新论文")
        logger.debug(f"论文获取阶段完成，准备进行数据验证...")
        
        if not all_papers:
            logger.info("没有找到新论文，程序结束")
            return
        
        # 验证论文数据
        logger.info("验证论文数据...")
        valid_papers = []
        validation_failed_count = 0
        
        for i, paper in enumerate(all_papers, 1):
            logger.debug(f"验证论文 {i}/{len(all_papers)}: {paper.title[:50]}...")
            if validator.validate_paper(paper):
                valid_papers.append(paper)
                logger.debug(f"  ✅ 验证通过")
            else:
                validation_failed_count += 1
                logger.debug(f"  ❌ 验证失败")
                if not args.dry_run:
                    cache_manager.mark_paper_failed(paper.url, paper.title, "数据验证失败")
                else:
                    logger.debug(f"  干运行模式，跳过缓存写入")
        
        logger.info(f"数据验证通过: {len(valid_papers)} 篇论文")
        logger.debug(f"验证统计 - 通过: {len(valid_papers)}, 失败: {validation_failed_count}")
        
        if not valid_papers:
            logger.info("没有有效的论文数据，程序结束")
            return
        
        # 分类论文（如果没有分类器则跳过）
        if classifier:
            logger.info("开始分类论文...")
            classification_config = config['classification_prompts']['classification_prompts']
            categories_config = classification_config['categories']
            logger.debug(f"加载分类配置: {len(categories_config)} 个类别")
            
            classified_papers = {}
            classification_stats = {'success': 0, 'failed': 0, 'rejected': 0, 'total': len(valid_papers)}
            
            for i, paper in enumerate(valid_papers, 1):
                logger.info(f"分类论文 {i}/{len(valid_papers)}: {paper.title[:50]}...")
                logger.debug(f"  论文作者: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
                logger.debug(f"  发布日期: {paper.publish_date.strftime('%Y-%m-%d')}")
                logger.debug(f"  摘要长度: {len(paper.abstract)} 字符")
                
                try:
                    logger.debug(f"  开始调用分类器...")
                    classification = classifier.classify_paper(paper, categories_config)
                    logger.debug(f"  分类器返回结果: {classification.category}/{classification.subcategory}")
                    
                    # 检查是否为拒绝分类
                    if classification.category == "REJECT":
                        logger.info(f"  -> 论文被拒绝: {classification.reasoning}")
                        # 标记为已处理但不包含在最终结果中
                        if not args.dry_run:
                            cache_manager.mark_paper_processed(
                                paper.url, paper.title, 
                                "REJECTED", 0.0,
                                reasoning=f"拒绝分类: {classification.reasoning}",
                                chinese_title=classification.chinese_title or "",
                                authors=paper.authors,
                                abstract=paper.abstract
                            )
                        else:
                            logger.debug(f"  干运行模式，跳过缓存写入")
                        
                        classification_stats['rejected'] += 1
                        continue  # 跳过此论文，不加入分类结果
                    
                    processed_paper = processor.process_paper(paper, classification)
                    logger.debug(f"  论文处理完成")
                    
                    # 验证处理后的论文
                    if validator.validate_processed_paper(processed_paper):
                        category_key = f"{classification.category}_{classification.subcategory}"
                        if category_key not in classified_papers:
                            classified_papers[category_key] = []
                        classified_papers[category_key].append(processed_paper)
                        
                        # 标记为已处理（仅在非干运行模式下）
                        if not args.dry_run:
                            cache_manager.mark_paper_processed(
                                paper.url, paper.title, 
                                classification.subcategory, classification.confidence,
                                reasoning=classification.reasoning,
                                chinese_title=classification.chinese_title or "",
                                authors=paper.authors,
                                abstract=paper.abstract
                            )
                        else:
                            logger.debug(f"  干运行模式，跳过缓存写入")
                        
                        classification_stats['success'] += 1
                        logger.info(f"  -> 分类为: {classification.subcategory} (置信度: {classification.confidence:.2f})")
                        logger.debug(f"  -> 分类推理: {classification.reasoning[:100]}...")
                    else:
                        if not args.dry_run:
                            cache_manager.mark_paper_failed(paper.url, paper.title, "处理后验证失败")
                        else:
                            logger.debug(f"  干运行模式，跳过缓存写入")
                        classification_stats['failed'] += 1
                    
                except Exception as e:
                    logger.error(f"论文分类失败: {paper.title[:50]}... - {e}")
                    logger.debug(f"分类失败详细信息: {str(e)}", exc_info=True)
                    if not args.dry_run:
                        cache_manager.mark_paper_failed(paper.url, paper.title, str(e))
                    else:
                        logger.debug(f"  干运行模式，跳过缓存写入")
                    classification_stats['failed'] += 1
                    continue
                
                # 避免API调用过于频繁
                logger.debug(f"等待0.5秒避免API调用过于频繁...")
                time.sleep(0.5)
            
            logger.info(f"分类完成: 成功 {classification_stats['success']}, 失败 {classification_stats['failed']}, 拒绝 {classification_stats['rejected']}")

        else:
            logger.warning("未初始化分类器，跳过分类步骤")
            # 在没有分类器的情况下，直接使用验证后的论文
            classified_papers = {'unknown_unknown': []}
            for paper in valid_papers:
                # 创建一个简单的处理后论文对象
                from processors.paper_processor import ProcessedPaper
                processed_paper = ProcessedPaper(
                    title=paper.title,
                    authors=paper.authors,
                    abstract=paper.abstract,
                    url=paper.url,
                    publish_date=paper.publish_date,
                    venue=paper.venue,
                    keywords=paper.keywords,
                    category="unknown",
                    subcategory="unknown",
                    confidence=0.0,
                    reasoning="未进行分类（缺少API密钥）"
                )
                classified_papers['unknown_unknown'].append(processed_paper)
        
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
            # 使用第一个updater进行预览
            preview = updaters[0][1].preview_changes(final_classified_papers)
            print("\n" + preview + "\n")
        
        # 更新README
        if not args.dry_run:
            logger.info("开始更新README文件...")
            
            # 对每个updater进行更新
            total_added_all = 0
            for lang, updater in updaters:
                logger.info(f"更新{lang.upper()}README文件: {updater.readme_path}")
                
                # 创建备份
                backup_path = updater.backup_readme()
                if backup_path:
                    logger.info(f"{lang.upper()}README备份已创建: {backup_path}")
                
                # 更新各分类
                total_added = 0
                for category_key, papers in final_classified_papers.items():
                    if papers:
                        category, subcategory = category_key.split('_', 1)
                        success = updater.add_papers_to_category(papers, category, subcategory)
                        if success:
                            total_added += len(papers)
                            logger.info(f"成功向{lang.upper()}版本的 {subcategory} 添加 {len(papers)} 篇论文")
                        else:
                            logger.error(f"向{lang.upper()}版本的 {subcategory} 添加论文失败")
                
                # 更新统计信息
                if total_added > 0:
                    current_counts = updater.count_existing_papers()
                    total_papers = current_counts.get('total', 0)
                    
                    updater.update_statistics(total_added, total_papers)
                    logger.info(f"{lang.upper()}版本统计信息已更新: 新增 {total_added} 篇论文，总计 {total_papers} 篇")
                    
                    if lang == "en":
                        total_added_all = total_added  # 使用英文版的总数作为最终统计
            
            logger.info(f"README文件更新完成，共更新了 {len(updaters)} 个文件")
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