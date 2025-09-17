import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import time
from urllib.parse import quote

from .base_crawler import BaseCrawler, Paper

class ArxivCrawler(BaseCrawler):
    """arXiv论文爬虫"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://export.arxiv.org/api/query')
        self.logger = logging.getLogger(__name__)
        
    def search_papers(self, query: str, max_results: int = 50) -> List[Paper]:
        """从arXiv搜索论文"""
        self.logger.info(f"从arXiv搜索论文: {query}")
        
        # 构建搜索参数
        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            # 发送请求
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析XML响应
            papers = self._parse_arxiv_response(response.text)
            
            # 过滤与网络安全相关的论文
            filtered_papers = [p for p in papers if self.is_cybersecurity_related(p)]
            
            self.logger.info(f"从arXiv获取到 {len(papers)} 篇论文，筛选出 {len(filtered_papers)} 篇网络安全相关论文")
            return filtered_papers
            
        except Exception as e:
            self.logger.error(f"arXiv搜索失败: {e}")
            return []
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Paper]:
        """解析arXiv API响应"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # arXiv API使用Atom命名空间
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                # 提取基本信息
                title_elem = entry.find('atom:title', ns)
                if title_elem is None:
                    continue
                    
                title = title_elem.text.strip().replace('\n', ' ').replace('  ', ' ') if title_elem.text else ""
                
                summary_elem = entry.find('atom:summary', ns)
                abstract = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else ""
                
                # 获取作者
                authors = []
                for author in entry.findall('atom:author', ns):
                    name_elem = author.find('atom:name', ns)
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text.strip())
                
                # 获取URL
                id_elem = entry.find('atom:id', ns)
                url = id_elem.text if id_elem is not None and id_elem.text else ""
                
                # 转换为PDF链接
                if url and 'abs' in url:
                    pdf_url = url.replace('/abs/', '/pdf/') + '.pdf'
                else:
                    pdf_url = url or ""
                
                # 获取发布日期
                published_elem = entry.find('atom:published', ns)
                if published_elem is not None and published_elem.text:
                    try:
                        publish_date = datetime.fromisoformat(
                            published_elem.text.replace('Z', '+00:00')
                        )
                    except:
                        publish_date = datetime.now()
                else:
                    publish_date = datetime.now()
                
                # 获取分类标签
                categories = []
                for category in entry.findall('atom:category', ns):
                    term = category.get('term')
                    if term:
                        categories.append(term)
                
                paper = Paper(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    url=pdf_url,
                    publish_date=publish_date,
                    venue="arXiv",
                    keywords=categories
                )
                
                papers.append(paper)
                
        except ET.ParseError as e:
            self.logger.error(f"XML解析错误: {e}")
        except Exception as e:
            self.logger.error(f"响应解析失败: {e}")
            
        return papers
    
    def get_paper_details(self, paper_id: str) -> Optional[Paper]:
        """获取特定论文的详细信息"""
        # arXiv ID格式: 2301.12345
        query = f"id:{paper_id}"
        papers = self.search_papers(query, max_results=1)
        return papers[0] if papers else None
    
    def is_cybersecurity_related(self, paper: Paper) -> bool:
        """判断论文是否与网络安全和LLM相关"""
        # 网络安全关键词
        cybersec_keywords = [
            'cybersecurity', 'cyber security', 'network security',
            'information security', 'vulnerability', 'malware',
            'intrusion detection', 'penetration testing', 'threat',
            'security analysis', 'attack', 'exploit', 'phishing',
            'fraud detection', 'anomaly detection', 'forensics',
            'cryptography', 'privacy', 'authentication', 'authorization'
        ]
        
        # AI/ML关键词  
        ai_keywords = [
            'large language model', 'LLM', 'GPT', 'BERT', 'transformer',
            'natural language processing', 'NLP', 'machine learning',
            'deep learning', 'artificial intelligence', 'AI',
            'neural network', 'fine-tuning', 'pre-trained'
        ]
        
        # 组合文本
        text = f"{paper.title} {paper.abstract}".lower()
        
        # 检查是否包含网络安全和AI相关关键词
        has_cybersec = any(keyword.lower() in text for keyword in cybersec_keywords)
        has_ai = any(keyword.lower() in text for keyword in ai_keywords)
        
        return has_cybersec and has_ai
    
    def get_recent_papers(self, days: int = 7) -> List[Paper]:
        """获取最近几天的论文"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        all_papers = []
        for query in self.config.get('search_terms', []):
            papers = self.search_papers(query, self.config.get('max_results', 50))
            all_papers.extend(papers)
            
            # 避免请求过于频繁
            time.sleep(1)
        
        # 过滤日期并去重
        recent_papers = []
        seen_urls = set()
        
        for paper in all_papers:
            if paper.publish_date >= cutoff_date and paper.url not in seen_urls:
                recent_papers.append(paper)
                seen_urls.add(paper.url)
        
        return recent_papers