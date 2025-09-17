import re
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.base_crawler import Paper
from processors.paper_processor import ProcessedPaper

class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_paper(self, paper: Paper) -> bool:
        """验证论文数据的有效性"""
        try:
            # 检查必要字段
            if not paper.title or not paper.abstract:
                self.logger.warning(f"论文缺少标题或摘要: {paper.title[:50] if paper.title else 'No title'}")
                return False
            
            # 检查标题长度
            if len(paper.title.strip()) < 10:
                self.logger.warning(f"论文标题过短: {paper.title}")
                return False
            
            # 检查摘要长度
            if len(paper.abstract.strip()) < 50:
                self.logger.warning(f"论文摘要过短: {paper.title[:50]}...")
                return False
            
            # 检查URL格式
            if not self.validate_url(paper.url):
                self.logger.warning(f"无效的URL: {paper.url}")
                return False
            
            # 检查发布日期
            if not isinstance(paper.publish_date, datetime):
                self.logger.warning(f"无效的发布日期: {paper.publish_date}")
                return False
            
            # 检查作者信息
            if not paper.authors or len(paper.authors) == 0:
                self.logger.warning(f"论文缺少作者信息: {paper.title[:50]}...")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"论文数据验证失败: {e}")
            return False
    
    def validate_url(self, url: str) -> bool:
        """验证URL格式和可访问性"""
        if not url:
            return False
        
        # 基本URL格式检查
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False
        
        # 检查常见学术网站
        academic_domains = [
            'arxiv.org',
            'dl.acm.org', 
            'ieeexplore.ieee.org',
            'link.springer.com',
            'scholar.google.com',
            'researchgate.net',
            'github.com'
        ]
        
        for domain in academic_domains:
            if domain in url.lower():
                return True
        
        # 对于其他域名，可以尝试简单的连接测试（可选）
        return True
    
    def validate_processed_paper(self, paper: ProcessedPaper) -> bool:
        """验证处理后的论文数据"""
        try:
            # 检查分类信息
            if not paper.category or not paper.subcategory:
                self.logger.warning(f"论文缺少分类信息: {paper.title[:50]}...")
                return False
            
            # 检查置信度
            if not (0.0 <= paper.confidence <= 1.0):
                self.logger.warning(f"无效的置信度: {paper.confidence}")
                return False
            
            # 检查venue
            if not paper.venue:
                self.logger.warning(f"论文缺少venue信息: {paper.title[:50]}...")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"处理后论文数据验证失败: {e}")
            return False
    
    def validate_config(self, config: Dict) -> bool:
        """验证配置文件"""
        try:
            # 检查必要的配置项
            required_keys = ['sources', 'classification_prompts', 'llm_config']
            
            for key in required_keys:
                if key not in config:
                    self.logger.error(f"配置文件缺少必要项: {key}")
                    return False
            
            # 验证数据源配置
            if 'sources' in config and 'data_sources' in config['sources']:
                if not self.validate_data_sources_config(config['sources']['data_sources']):
                    return False
            else:
                self.logger.warning("数据源配置缺失")
            
            # 验证LLM配置
            if not self.validate_llm_config(config.get('llm_config', {})):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False
    
    def validate_data_sources_config(self, sources_config: Dict) -> bool:
        """验证数据源配置"""
        for source_name, source_config in sources_config.items():
            if not isinstance(source_config, dict):
                self.logger.error(f"数据源配置格式错误: {source_name}")
                return False
            
            # 检查必要字段
            required_fields = ['enabled', 'base_url', 'search_terms']
            for field in required_fields:
                if field not in source_config:
                    self.logger.error(f"数据源 {source_name} 缺少必要字段: {field}")
                    return False
            
            # 验证搜索词
            if not isinstance(source_config['search_terms'], list):
                self.logger.error(f"数据源 {source_name} 的search_terms必须是列表")
                return False
        
        return True
    
    def validate_llm_config(self, llm_config: Dict) -> bool:
        """验证LLM配置"""
        # 检查是否有至少一个可用的LLM配置
        llm_providers = ['openai', 'claude', 'qwen', 'zhipu']
        has_valid_provider = False
        
        for provider in llm_providers:
            if provider in llm_config:
                provider_config = llm_config[provider]
                if 'api_key' in provider_config and provider_config['api_key']:
                    has_valid_provider = True
                    break
        
        if not has_valid_provider:
            self.logger.error("没有找到有效的LLM提供商配置")
            return False
        
        return True
    
    def sanitize_text(self, text: str) -> str:
        """清理和标准化文本"""
        if not text:
            return ""
        
        # 移除控制字符
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # 标准化空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除可能导致markdown格式问题的字符
        text = text.replace('[', '\\[').replace(']', '\\]')
        
        return text
    
    def validate_markdown_format(self, content: str) -> bool:
        """验证markdown格式"""
        try:
            # 检查基本markdown结构
            if not re.search(r'^#+ ', content, re.MULTILINE):
                self.logger.warning("内容缺少markdown标题")
                return False
            
            # 检查链接格式
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)
            
            for link_text, link_url in links:
                if not self.validate_url(link_url):
                    self.logger.warning(f"发现无效链接: {link_url}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Markdown格式验证失败: {e}")
            return False
    
    def check_duplicate_papers(self, papers: List[ProcessedPaper]) -> List[ProcessedPaper]:
        """检查并移除重复论文"""
        seen_titles = set()
        seen_urls = set()
        unique_papers = []
        duplicates = []
        
        for paper in papers:
            title_normalized = self.sanitize_text(paper.title).lower()
            
            if title_normalized in seen_titles or paper.url in seen_urls:
                duplicates.append(paper)
                self.logger.info(f"发现重复论文: {paper.title[:50]}...")
            else:
                unique_papers.append(paper)
                seen_titles.add(title_normalized)
                seen_urls.add(paper.url)
        
        if duplicates:
            self.logger.info(f"移除了 {len(duplicates)} 篇重复论文")
        
        return unique_papers
    
    def validate_classification_consistency(self, papers: List[ProcessedPaper]) -> bool:
        """验证分类一致性"""
        # 检查分类分布是否合理
        category_counts = {}
        low_confidence_count = 0
        
        for paper in papers:
            category = paper.subcategory
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
            
            if paper.confidence < 0.5:
                low_confidence_count += 1
        
        # 警告低置信度论文过多
        if low_confidence_count > len(papers) * 0.3:
            self.logger.warning(f"低置信度论文比例过高: {low_confidence_count}/{len(papers)}")
        
        # 警告某个分类论文过多
        for category, count in category_counts.items():
            if count > len(papers) * 0.5:
                self.logger.warning(f"分类 {category} 论文比例过高: {count}/{len(papers)}")
        
        return True