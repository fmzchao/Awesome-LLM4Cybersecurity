import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, Any, List
import logging

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        self.logger = logging.getLogger(__name__)
        
        # 创建缓存目录
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # 缓存文件路径
        self.processed_papers_file = os.path.join(cache_dir, "processed_papers.json")
        self.failed_papers_file = os.path.join(cache_dir, "failed_papers.json")
        self.api_cache_file = os.path.join(cache_dir, "api_cache.json")
        
        # 加载缓存数据
        self.processed_papers = self._load_cache(self.processed_papers_file)
        self.failed_papers = self._load_cache(self.failed_papers_file)
        self.api_cache = self._load_cache(self.api_cache_file)
    
    def _load_cache(self, file_path: str) -> Dict:
        """加载缓存文件"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"加载缓存文件失败 {file_path}: {e}")
        return {}
    
    def _save_cache(self, data: Dict, file_path: str):
        """保存缓存文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存缓存文件失败 {file_path}: {e}")
    
    def _generate_paper_key(self, paper_url: str, paper_title: str = "") -> str:
        """生成论文的缓存键"""
        # 基于URL和标题生成唯一键
        key_str = f"{paper_url}_{paper_title}".lower()
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def is_paper_processed(self, paper_url: str, paper_title: str = "") -> bool:
        """检查论文是否已经处理过"""
        key = self._generate_paper_key(paper_url, paper_title)
        return key in self.processed_papers
    
    def mark_paper_processed(self, paper_url: str, paper_title: str = "", 
                           category: str = "", confidence: float = 0.0,
                           reasoning: str = "", chinese_title: str = "",
                           authors: Optional[List[str]] = None, abstract: str = ""):
        """标记论文为已处理"""
        key = self._generate_paper_key(paper_url, paper_title)
        cache_data = {
            'url': paper_url,
            'title': paper_title,
            'category': category,
            'confidence': confidence,
            'processed_at': datetime.now().isoformat()
        }
        
        # 添加可选的详细信息
        if reasoning:
            cache_data['reasoning'] = reasoning
        if chinese_title:
            cache_data['chinese_title'] = chinese_title
        if authors:
            cache_data['authors'] = authors[:5]  # 最多保存5个作者
        if abstract:
            cache_data['abstract'] = abstract[:200] + '...' if len(abstract) > 200 else abstract
            
        self.processed_papers[key] = cache_data
        self._save_cache(self.processed_papers, self.processed_papers_file)
    
    def is_paper_failed(self, paper_url: str, paper_title: str = "") -> bool:
        """检查论文是否处理失败过"""
        key = self._generate_paper_key(paper_url, paper_title)
        if key not in self.failed_papers:
            return False
        
        # 检查失败时间，如果超过24小时则重新尝试
        failed_info = self.failed_papers[key]
        failed_time = datetime.fromisoformat(failed_info['failed_at'])
        return datetime.now() - failed_time < timedelta(hours=24)
    
    def mark_paper_failed(self, paper_url: str, paper_title: str = "", 
                         error: str = ""):
        """标记论文处理失败"""
        key = self._generate_paper_key(paper_url, paper_title)
        self.failed_papers[key] = {
            'url': paper_url,
            'title': paper_title,
            'error': error,
            'failed_at': datetime.now().isoformat()
        }
        self._save_cache(self.failed_papers, self.failed_papers_file)
    
    def cache_api_response(self, api_key: str, response_data: Any, 
                          expiry_hours: int = 24):
        """缓存API响应"""
        cache_key = hashlib.md5(api_key.encode('utf-8')).hexdigest()
        self.api_cache[cache_key] = {
            'data': response_data,
            'cached_at': datetime.now().isoformat(),
            'expiry_hours': expiry_hours
        }
        self._save_cache(self.api_cache, self.api_cache_file)
    
    def get_cached_api_response(self, api_key: str) -> Optional[Any]:
        """获取缓存的API响应"""
        cache_key = hashlib.md5(api_key.encode('utf-8')).hexdigest()
        
        if cache_key not in self.api_cache:
            return None
        
        cached_item = self.api_cache[cache_key]
        cached_time = datetime.fromisoformat(cached_item['cached_at'])
        expiry_hours = cached_item.get('expiry_hours', 24)
        
        # 检查是否过期
        if datetime.now() - cached_time > timedelta(hours=expiry_hours):
            del self.api_cache[cache_key]
            self._save_cache(self.api_cache, self.api_cache_file)
            return None
        
        return cached_item['data']
    
    def clean_expired_cache(self):
        """清理过期缓存"""
        current_time = datetime.now()
        
        # 清理过期的失败记录（超过7天）
        expired_failed = []
        for key, failed_info in self.failed_papers.items():
            failed_time = datetime.fromisoformat(failed_info['failed_at'])
            if current_time - failed_time > timedelta(days=7):
                expired_failed.append(key)
        
        for key in expired_failed:
            del self.failed_papers[key]
        
        if expired_failed:
            self._save_cache(self.failed_papers, self.failed_papers_file)
            self.logger.info(f"清理了 {len(expired_failed)} 条过期失败记录")
        
        # 清理过期的API缓存
        expired_api = []
        for key, cached_item in self.api_cache.items():
            cached_time = datetime.fromisoformat(cached_item['cached_at'])
            expiry_hours = cached_item.get('expiry_hours', 24)
            if current_time - cached_time > timedelta(hours=expiry_hours):
                expired_api.append(key)
        
        for key in expired_api:
            del self.api_cache[key]
        
        if expired_api:
            self._save_cache(self.api_cache, self.api_cache_file)
            self.logger.info(f"清理了 {len(expired_api)} 条过期API缓存")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        return {
            'processed_papers': len(self.processed_papers),
            'failed_papers': len(self.failed_papers),
            'api_cache_entries': len(self.api_cache),
            'cache_dir': self.cache_dir
        }
    
    def clear_all_cache(self):
        """清空所有缓存"""
        self.processed_papers.clear()
        self.failed_papers.clear()
        self.api_cache.clear()
        
        self._save_cache(self.processed_papers, self.processed_papers_file)
        self._save_cache(self.failed_papers, self.failed_papers_file)
        self._save_cache(self.api_cache, self.api_cache_file)
        
        self.logger.info("已清空所有缓存")