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
        self.logger.debug(f"搜索参数 - 最大结果数: {max_results}")
        
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
            self.logger.debug(f"发送请求到: {self.base_url}")
            self.logger.debug(f"请求参数: {params}")
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            self.logger.debug(f"收到响应，状态码: {response.status_code}")
            self.logger.debug(f"响应内容长度: {len(response.text)} 字符")
            
            # 解析XML响应
            self.logger.debug("开始解析XML响应...")
            papers = self._parse_arxiv_response(response.text)
            self.logger.debug(f"XML解析完成，获得 {len(papers)} 篇论文")
            
            # 过滤与网络安全相关的论文
            self.logger.debug("开始过滤网络安全相关论文...")
            filtered_papers = []
            for i, paper in enumerate(papers, 1):
                if self.is_cybersecurity_related(paper):
                    filtered_papers.append(paper)
                    self.logger.debug(f"  ✅ 第{i}篇相关: {paper.title[:50]}...")
                else:
                    self.logger.debug(f"  ❌ 第{i}篇不相关: {paper.title[:50]}...")
            
            self.logger.info(f"从arXiv获取到 {len(papers)} 篇论文，筛选出 {len(filtered_papers)} 篇网络安全相关论文")
            return filtered_papers
            
        except requests.exceptions.Timeout as e:
            self.logger.error(f"arXiv请求超时: {e}")
            return []
        except requests.exceptions.RequestException as e:
            self.logger.error(f"arXiv网络请求失败: {e}")
            return []
        except Exception as e:
            self.logger.error(f"arXiv搜索失败: {e}")
            self.logger.debug(f"arXiv搜索详细错误: {str(e)}", exc_info=True)
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
                        # 转换为无时区的日期时间，方便后续比较
                        publish_date = publish_date.replace(tzinfo=None)
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
        """判断论文是否与网络安全和LLM相关
        
        注意：为了避免关键词匹配的误报和漏报问题，
        现在所有论文都会被保留，由GPT进行更精确的分类和筛选。
        """
        # 直接返回True，让所有论文都交给GPT判断
        return True
    
    def get_recent_papers(self, days: int = 7, total_limit: Optional[int] = None) -> List[Paper]:
        """获取最近几天的论文
        
        Args:
            days: 获取最近几天的论文
            total_limit: 总论文数量限制（可选），如果设置则在达到数量后停止搜索
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        self.logger.debug(f"获取 {days} 天内的论文，截止日期: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        search_terms = self.config.get('search_terms', [])
        max_results = self.config.get('max_results', 50)
        
        if total_limit:
            self.logger.debug(f"将使用 {len(search_terms)} 个搜索词，每个最多获取 {max_results} 篇论文，总数限制: {total_limit}")
        else:
            self.logger.debug(f"将使用 {len(search_terms)} 个搜索词，每个最多获取 {max_results} 篇论文")
        
        # 存储所有获取的论文（未过滤时间）
        all_papers = []
        # 存储过滤后的有效论文
        valid_papers = []
        seen_urls = set()
        
        for i, query in enumerate(search_terms, 1):
            # 检查是否已经达到有效论文总数限制
            if total_limit and len(valid_papers) >= total_limit:
                self.logger.debug(f"已达到有效论文总数限制 {total_limit}，停止搜索")
                break
                
            self.logger.debug(f"正在搜索 {i}/{len(search_terms)}: {query}")
            
            # 获取论文
            papers = self.search_papers(query, max_results)
            all_papers.extend(papers)
            self.logger.debug(f"搜索词 '{query}' 获得 {len(papers)} 篇相关论文")
            
            # 立即过滤并统计有效论文
            new_valid_count = 0
            old_papers_count = 0
            duplicate_count = 0
            
            for paper in papers:
                if paper.publish_date < cutoff_date:
                    old_papers_count += 1
                    continue
                    
                if paper.url in seen_urls:
                    duplicate_count += 1
                    continue
                    
                valid_papers.append(paper)
                seen_urls.add(paper.url)
                new_valid_count += 1
                
                # 检查是否已经达到总数限制
                if total_limit and len(valid_papers) >= total_limit:
                    self.logger.debug(f"搜索词 '{query}' 处理过程中达到有效论文总数限制 {total_limit}，停止当前搜索词处理")
                    break
            
            self.logger.debug(f"搜索词 '{query}' 过滤结果: 新增有效 {new_valid_count} 篇，过旧 {old_papers_count} 篇，重复 {duplicate_count} 篇")
            self.logger.debug(f"当前累计有效论文数: {len(valid_papers)}")
            
            # 检查是否已经达到总数限制
            if total_limit and len(valid_papers) >= total_limit:
                self.logger.debug(f"已达到有效论文总数限制 {total_limit}，停止搜索")
                break
            
            # 避免请求过于频繁
            if i < len(search_terms):  # 不是最后一个
                self.logger.debug("等待1秒避免请求过于频繁...")
                time.sleep(1)
        
        self.logger.debug(f"所有搜索词总共获得 {len(all_papers)} 篇原始论文，{len(valid_papers)} 篇有效论文")
        
        # 统计最终结果
        old_papers_count = len(all_papers) - len(valid_papers) 
        duplicate_count = 0  # 重复统计已经在循环中处理
        
        self.logger.info(f"过滤结果: 保留 {len(valid_papers)} 篇，过旧 {old_papers_count} 篇，重复 {duplicate_count} 篇")
        return valid_papers