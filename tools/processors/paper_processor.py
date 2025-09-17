from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import logging
from typing import List, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.base_crawler import Paper
from classifiers.base_classifier import ClassificationResult

@dataclass
class ProcessedPaper:
    """处理后的论文数据"""
    title: str
    authors: List[str]
    abstract: str
    url: str
    publish_date: datetime
    venue: str
    category: str
    subcategory: str
    confidence: float
    keywords: List[str]
    reasoning: str
    chinese_title: Optional[str] = None  # 中文标题

class PaperProcessor:
    """论文数据处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_paper(self, paper: Paper, classification: ClassificationResult) -> ProcessedPaper:
        """处理单篇论文"""
        
        # 清理和标准化数据
        cleaned_title = self._clean_title(paper.title)
        cleaned_abstract = self._clean_abstract(paper.abstract)
        standardized_venue = self._standardize_venue(paper.venue)
        formatted_authors = self._format_authors(paper.authors)
        
        return ProcessedPaper(
            title=cleaned_title,
            authors=formatted_authors,
            abstract=cleaned_abstract,
            url=paper.url,
            publish_date=paper.publish_date,
            venue=standardized_venue,
            category=classification.category,
            subcategory=classification.subcategory,
            confidence=classification.confidence,
            keywords=paper.keywords or [],
            reasoning=classification.reasoning,
            chinese_title=classification.chinese_title
        )
    
    def process_papers_batch(self, papers: List[Paper], classifications: List[ClassificationResult]) -> List[ProcessedPaper]:
        """批量处理论文"""
        if len(papers) != len(classifications):
            raise ValueError("论文数量与分类结果数量不匹配")
        
        processed_papers = []
        for paper, classification in zip(papers, classifications):
            try:
                processed_paper = self.process_paper(paper, classification)
                processed_papers.append(processed_paper)
            except Exception as e:
                self.logger.error(f"处理论文失败: {paper.title[:50]}... - {e}")
                continue
        
        return processed_papers
    
    def _clean_title(self, title: str) -> str:
        """清理论文标题"""
        if not title:
            return ""
        
        # 移除多余的空白字符
        title = re.sub(r'\s+', ' ', title.strip())
        
        # 移除常见的格式标记
        title = re.sub(r'^\s*\[.*?\]\s*', '', title)  # 移除开头的标签
        title = re.sub(r'\s*\(.*?arXiv.*?\)\s*$', '', title)  # 移除结尾的arXiv标记
        
        # 确保标题不为空
        if not title.strip():
            return "Untitled Paper"
        
        return title.strip()
    
    def _clean_abstract(self, abstract: str) -> str:
        """清理论文摘要"""
        if not abstract:
            return ""
        
        # 移除多余的空白字符
        abstract = re.sub(r'\s+', ' ', abstract.strip())
        
        # 移除常见的前缀
        abstract = re.sub(r'^(Abstract[:\s]*|ABSTRACT[:\s]*)', '', abstract)
        
        # 限制长度（用于显示）
        if len(abstract) > 500:
            abstract = abstract[:497] + "..."
        
        return abstract.strip()
    
    def _standardize_venue(self, venue: str) -> str:
        """标准化发表venue"""
        if not venue:
            return "Unknown"
        
        # 常见venue映射
        venue_mapping = {
            'arxiv': 'arXiv',
            'acm': 'ACM',
            'ieee': 'IEEE',
            'usenix': 'USENIX',
            'ccs': 'ACM CCS',
            'ndss': 'NDSS',
            'sp': 'IEEE S&P',
            'icse': 'ICSE',
            'iclr': 'ICLR',
            'icml': 'ICML',
            'nips': 'NeurIPS',
            'neurips': 'NeurIPS'
        }
        
        venue_lower = venue.lower().strip()
        return venue_mapping.get(venue_lower, venue.strip())
    
    def _format_authors(self, authors: List[str]) -> List[str]:
        """格式化作者列表"""
        if not authors:
            return []
        
        formatted_authors = []
        for author in authors:
            if author and author.strip():
                # 移除多余空格
                author_clean = re.sub(r'\s+', ' ', author.strip())
                formatted_authors.append(author_clean)
        
        return formatted_authors
    
    def deduplicate_papers(self, papers: List[ProcessedPaper]) -> List[ProcessedPaper]:
        """去除重复论文"""
        seen_titles = set()
        seen_urls = set()
        unique_papers = []
        
        for paper in papers:
            # 基于标题和URL去重
            title_key = self._normalize_for_comparison(paper.title)
            
            if title_key not in seen_titles and paper.url not in seen_urls:
                unique_papers.append(paper)
                seen_titles.add(title_key)
                seen_urls.add(paper.url)
            else:
                self.logger.debug(f"发现重复论文: {paper.title[:50]}...")
        
        self.logger.info(f"去重前: {len(papers)} 篇论文，去重后: {len(unique_papers)} 篇论文")
        return unique_papers
    
    def _normalize_for_comparison(self, text: str) -> str:
        """标准化文本用于比较"""
        # 转换为小写，移除标点和多余空格
        normalized = re.sub(r'[^\w\s]', '', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized.strip())
        return normalized
    
    def filter_by_date_range(self, papers: List[ProcessedPaper], 
                           start_date: Optional[datetime] = None, 
                           end_date: Optional[datetime] = None) -> List[ProcessedPaper]:
        """按日期范围过滤论文"""
        filtered_papers = []
        
        for paper in papers:
            include = True
            
            if start_date and paper.publish_date < start_date:
                include = False
            
            if end_date and paper.publish_date > end_date:
                include = False
            
            if include:
                filtered_papers.append(paper)
        
        return filtered_papers
    
    def filter_by_confidence(self, papers: List[ProcessedPaper], 
                           min_confidence: float = 0.5) -> List[ProcessedPaper]:
        """按置信度过滤论文"""
        return [p for p in papers if p.confidence >= min_confidence]
    
    def sort_papers(self, papers: List[ProcessedPaper], 
                   sort_by: str = 'date', reverse: bool = True) -> List[ProcessedPaper]:
        """排序论文"""
        if sort_by == 'date':
            return sorted(papers, key=lambda p: p.publish_date, reverse=reverse)
        elif sort_by == 'confidence':
            return sorted(papers, key=lambda p: p.confidence, reverse=reverse)
        elif sort_by == 'title':
            return sorted(papers, key=lambda p: p.title.lower(), reverse=reverse)
        else:
            return papers
    
    def group_by_category(self, papers: List[ProcessedPaper]) -> Dict[str, List[ProcessedPaper]]:
        """按分类分组论文"""
        grouped = {}
        
        for paper in papers:
            category_key = f"{paper.category}_{paper.subcategory}"
            if category_key not in grouped:
                grouped[category_key] = []
            grouped[category_key].append(paper)
        
        return grouped
    
    def generate_statistics(self, papers: List[ProcessedPaper]) -> Dict:
        """生成统计信息"""
        stats = {
            'total_papers': len(papers),
            'by_category': {},
            'by_venue': {},
            'by_date': {},
            'confidence_distribution': {
                'high': 0,  # >= 0.8
                'medium': 0,  # 0.5-0.8
                'low': 0   # < 0.5
            },
            'average_confidence': 0.0
        }
        
        if not papers:
            return stats
        
        # 按分类统计
        for paper in papers:
            subcategory = paper.subcategory
            if subcategory not in stats['by_category']:
                stats['by_category'][subcategory] = 0
            stats['by_category'][subcategory] += 1
        
        # 按venue统计
        for paper in papers:
            venue = paper.venue
            if venue not in stats['by_venue']:
                stats['by_venue'][venue] = 0
            stats['by_venue'][venue] += 1
        
        # 按月份统计
        for paper in papers:
            month_key = paper.publish_date.strftime('%Y-%m')
            if month_key not in stats['by_date']:
                stats['by_date'][month_key] = 0
            stats['by_date'][month_key] += 1
        
        # 置信度分布
        total_confidence = 0
        for paper in papers:
            total_confidence += paper.confidence
            if paper.confidence >= 0.8:
                stats['confidence_distribution']['high'] += 1
            elif paper.confidence >= 0.5:
                stats['confidence_distribution']['medium'] += 1
            else:
                stats['confidence_distribution']['low'] += 1
        
        stats['average_confidence'] = total_confidence / len(papers)
        
        return stats