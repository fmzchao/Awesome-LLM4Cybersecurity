from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Paper:
    """论文数据结构"""
    title: str
    authors: List[str]
    abstract: str
    url: str
    publish_date: datetime
    venue: str
    keywords: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.name = self.__class__.__name__.replace('Crawler', '').lower()
    
    @abstractmethod
    def search_papers(self, query: str, max_results: int = 50) -> List[Paper]:
        """搜索论文"""
        pass
    
    @abstractmethod
    def get_paper_details(self, paper_id: str) -> Optional[Paper]:
        """获取论文详细信息"""
        pass
    
    def is_cybersecurity_related(self, paper: Paper) -> bool:
        """判断是否与网络安全相关"""
        cybersec_keywords = [
            'cybersecurity', 'cyber security', 'network security',
            'information security', 'vulnerability', 'malware',
            'intrusion detection', 'penetration testing', 'threat'
        ]
        
        text = f"{paper.title} {paper.abstract}".lower()
        return any(keyword in text for keyword in cybersec_keywords)
    
    def validate_paper(self, paper: Paper) -> bool:
        """验证论文数据的完整性"""
        if not paper.title or not paper.abstract:
            return False
        if len(paper.title) < 10 or len(paper.abstract) < 50:
            return False
        return True