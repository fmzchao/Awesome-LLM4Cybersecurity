import json
import logging
import requests
from typing import Dict, List
from .base_classifier import BaseClassifier, ClassificationResult

class OpenAIClassifier(BaseClassifier):
    def __init__(self, config: Dict, prompt_config_path: str = "config/classification_prompts.yaml"):
        super().__init__(config, prompt_config_path)
        self.api_key = config['api_key']
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.temperature = config.get('temperature', 0.1)
        self.max_tokens = config.get('max_tokens', 800)
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.logger = logging.getLogger(__name__)
    
    def classify_paper(self, paper, categories: Dict) -> ClassificationResult:
        """使用OpenAI API对论文进行分类"""
        
        # 构建详细的分类提示
        prompt = self._build_detailed_classification_prompt(paper, categories)
        
        try:
            # 使用requests直接调用OpenAI API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": self.prompt_config['classification_prompts']['system_prompt']
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result_text = response.json()['choices'][0]['message']['content'].strip()
            classification_result = self._parse_classification_result(result_text)
            
            # 应用优先级规则
            classification_result = self._apply_priority_rules(paper, classification_result)
            
            # 验证分类结果
            classification_result = self._validate_classification(classification_result)
            
            self.logger.info(f"论文 '{paper.title[:50]}...' 分类为: {classification_result.subcategory} (置信度: {classification_result.confidence})")
            
            return classification_result
            
        except Exception as e:
            self.logger.error(f"OpenAI分类失败: {e}")
            return ClassificationResult(
                category="rq2", 
                subcategory="Others", 
                confidence=0.0,
                reasoning=f"分类失败: {str(e)}"
            )
    
    def _build_detailed_classification_prompt(self, paper, categories: Dict) -> str:
        """构建详细的分类提示词"""
        
        # 构建分类描述
        categories_description = self._build_categories_description(
            self.prompt_config['classification_prompts']['categories']
        )
        
        # 获取基础提示词模板
        base_template = self.prompt_config['classification_prompts']['base_prompt_template']
        
        # 准备论文信息
        keywords = getattr(paper, 'keywords', []) or []
        keywords_str = ', '.join(keywords) if keywords else "无"
        
        # 填充模板
        prompt = base_template.format(
            title=paper.title,
            abstract=paper.abstract[:1000] + "..." if len(paper.abstract) > 1000 else paper.abstract,
            venue=getattr(paper, 'venue', 'Unknown'),
            keywords=keywords_str,
            categories_description=categories_description
        )
        
        # 添加额外的分类指导
        prompt += "\n\n" + self._build_classification_guidance()
        
        return prompt
    
    def _build_classification_guidance(self) -> str:
        """构建分类指导信息"""
        guidance = """
分类指导原则:
1. 仔细阅读论文标题和摘要，理解研究的核心内容
2. 优先根据研究的主要贡献和应用场景进行分类
3. 如果论文涉及多个领域，选择最主要的研究重点
4. 注意区分以下常见情况：
   - 如果是创建数据集或基准测试 → Cybersecurity Evaluation Benchmarks
   - 如果是训练或微调模型 → Fine-tuned Domain LLMs for Cybersecurity  
   - 如果是检测漏洞或安全问题 → Vulnerabilities Detection
   - 如果是修复代码或漏洞 → Program Repair
   - 如果是模糊测试相关 → FUZZ
   - 如果是威胁分析或情报 → Threat Intelligence
   - 如果是异常或入侵检测 → Anomaly Detection
   - 如果是攻击或渗透测试 → LLM Assisted Attack
   - 如果是智能体相关 → Further Research: Agent4Cybersecurity

5. 置信度评分标准：
   - 0.9-1.0: 非常确定，论文明确属于该分类
   - 0.7-0.8: 比较确定，论文主要内容符合该分类
   - 0.5-0.6: 中等确定，论文部分内容符合该分类
   - 0.3-0.4: 不太确定，分类可能不准确
   - 0.1-0.2: 很不确定，建议重新评估

请确保返回有效的JSON格式，包含所有必需字段。
"""
        return guidance
    
    def _parse_classification_result(self, result_text: str) -> ClassificationResult:
        """解析分类结果"""
        try:
            # 尝试提取JSON部分
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                json_text = result_text[json_start:json_end].strip()
            elif "{" in result_text and "}" in result_text:
                json_start = result_text.find("{")
                json_end = result_text.rfind("}") + 1
                json_text = result_text[json_start:json_end].strip()
            else:
                raise ValueError("未找到有效的JSON格式")
            
            result_data = json.loads(json_text)
            
            return ClassificationResult(
                category=result_data.get('category', 'rq2'),
                subcategory=result_data.get('subcategory', 'Others'),
                confidence=float(result_data.get('confidence', 0.5)),
                reasoning=result_data.get('reasoning', 'AI分类结果')
            )
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.warning(f"解析分类结果失败: {e}, 原始结果: {result_text}")
            
            # 尝试基于关键词的简单分类
            return self._fallback_classification(result_text)
    
    def _fallback_classification(self, text: str) -> ClassificationResult:
        """备用分类方法"""
        text_lower = text.lower()
        
        # 基于关键词的简单匹配
        if any(word in text_lower for word in ['benchmark', 'dataset', 'evaluation']):
            return ClassificationResult("rq1", "Cybersecurity Evaluation Benchmarks", 0.6, "基于关键词的备用分类")
        elif any(word in text_lower for word in ['fine-tun', 'training', 'model']):
            return ClassificationResult("rq1", "Fine-tuned Domain LLMs for Cybersecurity", 0.6, "基于关键词的备用分类")
        elif any(word in text_lower for word in ['threat', 'intelligence', 'malware']):
            return ClassificationResult("rq2", "Threat Intelligence", 0.6, "基于关键词的备用分类")
        elif any(word in text_lower for word in ['fuzz', 'testing']):
            return ClassificationResult("rq2", "FUZZ", 0.6, "基于关键词的备用分类")
        elif any(word in text_lower for word in ['vulnerability', 'detection']):
            return ClassificationResult("rq2", "Vulnerabilities Detection", 0.6, "基于关键词的备用分类")
        elif any(word in text_lower for word in ['repair', 'fix', 'patch']):
            return ClassificationResult("rq2", "Program Repair", 0.6, "基于关键词的备用分类")
        elif any(word in text_lower for word in ['anomaly', 'intrusion', 'detection']):
            return ClassificationResult("rq2", "Anomaly Detection", 0.6, "基于关键词的备用分类")
        elif any(word in text_lower for word in ['attack', 'penetration', 'exploit']):
            return ClassificationResult("rq2", "LLM Assisted Attack", 0.6, "基于关键词的备用分类")
        elif any(word in text_lower for word in ['agent', 'autonomous']):
            return ClassificationResult("rq3", "Further Research: Agent4Cybersecurity", 0.6, "基于关键词的备用分类")
        else:
            return ClassificationResult("rq2", "Others", 0.3, "无法确定分类，归入Others")
    
    def batch_classify(self, papers: List, categories: Dict, batch_size: int = 5) -> List[ClassificationResult]:
        """批量分类论文"""
        results = []
        
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i + batch_size]
            self.logger.info(f"正在处理第 {i//batch_size + 1} 批论文 ({len(batch)} 篇)")
            
            for paper in batch:
                result = self.classify_paper(paper, categories)
                results.append(result)
                
            # 避免API调用过于频繁
            if i + batch_size < len(papers):
                import time
                time.sleep(1)
        
        return results