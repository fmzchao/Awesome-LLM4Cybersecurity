import re
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

from .paper_processor import ProcessedPaper

class ReadmeUpdater:
    """README.md文件更新器"""
    
    def __init__(self, readme_path: str = "README.md", language: str = "en"):
        self.readme_path = readme_path
        self.language = language  # "en" 或 "zh"
        self.logger = logging.getLogger(__name__)
        
        # 英文到中文分类名称映射
        self.en_to_zh_mapping = {
            "Cybersecurity Evaluation Benchmarks": "网络安全评测基准",
            "Fine-tuned Domain LLMs for Cybersecurity": "网络安全领域微调大模型",
            "Threat Intelligence": "威胁情报",
            "FUZZ": "模糊测试（FUZZ）",
            "Vulnerabilities Detection": "漏洞检测",
            "Insecure code Generation": "不安全代码生成",
            "Program Repair": "程序修复",
            "Anomaly Detection": "异常检测",
            "LLM Assisted Attack": "大模型辅助攻击",
            "Others": "其他应用",
            "Further Research: Agent4Cybersecurity": "进一步研究：Agent4Cybersecurity（网络安全智能体）"
        }
        
        # 确保文件存在
        if not os.path.exists(readme_path):
            raise FileNotFoundError(f"README文件不存在: {readme_path}")
    
    def add_papers_to_category(self, papers: List[ProcessedPaper], 
                             category: str, subcategory: str) -> bool:
        """将论文添加到指定分类中"""
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 找到对应的分类部分
            section_pattern = self._build_section_pattern(subcategory)
            match = re.search(section_pattern, content, re.MULTILINE | re.DOTALL)
            
            if not match:
                self.logger.warning(f"未找到分类: {subcategory}")
                return False
            
            # 获取现有论文编号
            existing_numbers = self._get_existing_paper_numbers(match.group(0))
            next_number = max(existing_numbers) + 1 if existing_numbers else 1
            
            # 生成新论文条目
            new_entries = []
            for paper in papers:
                entry = self._format_paper_entry(paper, next_number)
                new_entries.append(entry)
                next_number += 1
                self.logger.info(f"添加论文: {paper.title[:50]}... 到分类 {subcategory}")
            
            # 找到插入位置（该分类的最后一篇论文后）
            insertion_point = self._find_insertion_point(content, subcategory)
            
            if insertion_point == -1:
                self.logger.error(f"无法找到分类 {subcategory} 的插入位置")
                return False
            
            # 插入新条目
            new_content = (
                content[:insertion_point] + 
                '\n\n' + '\n\n'.join(new_entries) + 
                content[insertion_point:]
            )
            
            # 写回文件
            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.logger.info(f"成功添加 {len(new_entries)} 篇论文到 {subcategory}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新README失败: {e}")
            return False
    
    def _build_section_pattern(self, subcategory: str) -> str:
        """构建分类章节的正则表达式"""
        # 根据语言选择合适的分类名称
        if self.language == "zh" and subcategory in self.en_to_zh_mapping:
            target_subcategory = self.en_to_zh_mapping[subcategory]
        else:
            target_subcategory = subcategory
        
        # 转义特殊字符
        escaped_subcategory = re.escape(target_subcategory)
        
        # 匹配markdown标题
        pattern = f"####\\s+{escaped_subcategory}\\s*\n(.*?)(?=\n####|\n###|\n##|\\Z)"
        return pattern
    
    def _get_existing_paper_numbers(self, section_content: str) -> List[int]:
        """获取已存在的论文编号"""
        numbers = []
        
        # 匹配论文条目编号 (如: "1. Title")
        pattern = r'^\s*(\d+)\.\s+'
        matches = re.findall(pattern, section_content, re.MULTILINE)
        
        for match in matches:
            try:
                numbers.append(int(match))
            except ValueError:
                continue
        
        return numbers
    
    def _find_insertion_point(self, content: str, subcategory: str) -> int:
        """找到论文插入位置"""
        # 根据语言选择合适的分类名称
        if self.language == "zh" and subcategory in self.en_to_zh_mapping:
            target_subcategory = self.en_to_zh_mapping[subcategory]
        else:
            target_subcategory = subcategory
        
        # 首先找到subcategory的位置
        subcategory_pattern = f"####\\s+{re.escape(target_subcategory)}"
        subcategory_match = re.search(subcategory_pattern, content)
        
        if not subcategory_match:
            return -1
        
        start_pos = subcategory_match.end()
        
        # 从subcategory开始，找到下一个同级或更高级标题的位置
        next_section_pattern = r'\n(####|###|##)\s+'
        next_section_match = re.search(next_section_pattern, content[start_pos:])
        
        if next_section_match:
            # 在下一个section之前插入
            return start_pos + next_section_match.start()
        else:
            # 如果没有找到下一个section，在文件末尾插入
            return len(content)
    
    def _format_paper_entry(self, paper: ProcessedPaper, number: int) -> str:
        """格式化论文条目"""
        date_str = paper.publish_date.strftime("%Y.%m.%d")
        
        # 根据语言选择合适的标题
        if self.language == "zh":
            # 中文版优先使用中文标题，如果没有则使用英文标题
            title = getattr(paper, 'chinese_title', paper.title) or paper.title
            link_text = "论文链接"
        else:
            # 英文版使用英文标题
            title = paper.title
            link_text = "Paper Link"
        
        # 清理标题中可能导致markdown格式问题的字符
        clean_title = title.replace('[', '\\[').replace(']', '\\]')
        
        # 根据语言格式化条目
        if self.language == "zh":
            entry = f"{number}. {clean_title} ｜ *{paper.venue}* ｜ {date_str} ｜ [<u>{link_text}</u>]({paper.url})"
        else:
            entry = f"{number}. {clean_title} | *{paper.venue}* | {date_str} | [<u>{link_text}</u>]({paper.url})"
        
        return entry
    
    def update_statistics(self, new_papers_count: int, total_papers_count: Optional[int] = None) -> bool:
        """更新统计信息"""
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新最新更新日期
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 在🔥 Updates部分添加新的更新记录
            updates_pattern = r'(## 🔥 Updates\n)'
            new_update = f"📆[{today}] 通过自动化工具新增 *{new_papers_count}* 篇论文。\n\n"
            
            updated_content = re.sub(
                updates_pattern, 
                f"\\1{new_update}", 
                content, 
                count=1
            )
            
            # 如果提供了总论文数，更新Features部分的统计
            if total_papers_count:
                features_pattern = r'(\(2024\.08\.20\) Our study encompasses an analysis of over )\d+( works)'
                updated_content = re.sub(
                    features_pattern,
                    f"\\1{total_papers_count}\\2",
                    updated_content
                )
            
            # 写回文件
            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.logger.info(f"更新统计信息: 新增 {new_papers_count} 篇论文")
            return True
            
        except Exception as e:
            self.logger.error(f"更新统计信息失败: {e}")
            return False
    
    def backup_readme(self) -> str:
        """备份README文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.readme_path}.backup_{timestamp}"
        
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            self.logger.info(f"README备份创建: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            return ""
    
    def validate_readme_structure(self) -> bool:
        """验证README文件结构"""
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 根据语言选择需要检查的章节
            if self.language == "zh":
                required_sections = [
                    "## 🔥 更新日志",
                    "## 🌈 引言", 
                    "## 🚩 研究特性",
                    "## 🌟 文献汇总",
                    "### RQ1：",
                    "### RQ2：",
                    "### RQ3："
                ]
            else:
                required_sections = [
                    "## 🔥 Updates",
                    "## 🌈 Introduction", 
                    "## 🚩 Features",
                    "## 🌟 Literatures",
                    "### RQ1:",
                    "### RQ2:",
                    "### RQ3:"
                ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            if missing_sections:
                self.logger.warning(f"README缺少必要章节: {missing_sections}")
                return False
            
            self.logger.info("README结构验证通过")
            return True
            
        except Exception as e:
            self.logger.error(f"README结构验证失败: {e}")
            return False
    
    def count_existing_papers(self) -> Dict[str, int]:
        """统计现有论文数量"""
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 定义所有子分类
            subcategories = [
                "Cybersecurity Evaluation Benchmarks",
                "Fine-tuned Domain LLMs for Cybersecurity", 
                "Threat Intelligence",
                "FUZZ",
                "Vulnerabilities Detection",
                "Insecure code Generation",
                "Program Repair", 
                "Anomaly Detection",
                "LLM Assisted Attack",
                "Others",
                "Further Research: Agent4Cybersecurity"
            ]
            
            counts = {}
            total = 0
            
            for subcategory in subcategories:
                pattern = self._build_section_pattern(subcategory)
                match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
                
                if match:
                    section_content = match.group(1)
                    numbers = self._get_existing_paper_numbers(section_content)
                    count = len(numbers)
                    counts[subcategory] = count
                    total += count
                else:
                    counts[subcategory] = 0
            
            counts['total'] = total
            self.logger.info(f"现有论文统计完成，总计: {total} 篇")
            
            return counts
            
        except Exception as e:
            self.logger.error(f"统计现有论文失败: {e}")
            return {}
    
    def preview_changes(self, papers_by_category: Dict[str, List[ProcessedPaper]]) -> str:
        """预览将要进行的更改"""
        preview = ["=== 预览将要添加的论文 ===\n"]
        
        total_new_papers = 0
        for category_key, papers in papers_by_category.items():
            if papers:
                _, subcategory = category_key.split('_', 1)
                preview.append(f"## {subcategory} ({len(papers)} 篇)")
                
                for i, paper in enumerate(papers[:3], 1):  # 只显示前3篇
                    preview.append(f"  {i}. {paper.title[:80]}...")
                
                if len(papers) > 3:
                    preview.append(f"  ... 还有 {len(papers) - 3} 篇论文")
                
                preview.append("")
                total_new_papers += len(papers)
        
        preview.append(f"总计将新增: {total_new_papers} 篇论文")
        
        return "\n".join(preview)