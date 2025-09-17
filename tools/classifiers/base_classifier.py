import yaml
import json
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    category: str
    subcategory: str
    confidence: float
    reasoning: str

class BaseClassifier(ABC):
    def __init__(self, config: Dict, prompt_config_path: str = "config/classification_prompts.yaml"):
        self.config = config
        self.prompt_config = self._load_prompt_config(prompt_config_path)
        
    def _load_prompt_config(self, config_path: str) -> Dict:
        """加载提示词配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @abstractmethod
    def classify_paper(self, paper, categories: Dict) -> ClassificationResult:
        """对论文进行分类"""
        pass
    
    def _build_categories_description(self, categories: Dict) -> str:
        """构建分类描述文本"""
        descriptions = []
        
        for category_id, category_info in categories.items():
            descriptions.append(f"\n## {category_info['name']}")
            descriptions.append(f"描述: {category_info['description']}")
            
            for subcat_name, subcat_info in category_info['subcategories'].items():
                descriptions.append(f"\n### {subcat_name}")
                descriptions.append(f"说明: {subcat_info['description']}")
                descriptions.append(f"关键词: {', '.join(subcat_info['keywords'])}")
                if 'examples' in subcat_info:
                    descriptions.append(f"示例: {', '.join(subcat_info['examples'])}")
        
        return '\n'.join(descriptions)
    
    def _apply_priority_rules(self, paper, classification_result: ClassificationResult) -> ClassificationResult:
        """应用优先级规则"""
        text = f"{paper.title} {paper.abstract}".lower()
        
        # 检查优先关键词
        priority_keywords = self.prompt_config.get('special_rules', {}).get('priority_keywords', {})
        for keyword, preferred_category in priority_keywords.items():
            if keyword.lower() in text:
                # 如果找到优先关键词且当前置信度不高，则调整分类
                if classification_result.confidence < 0.8:
                    classification_result.subcategory = preferred_category
                    classification_result.confidence = min(classification_result.confidence + 0.2, 0.9)
                    classification_result.reasoning += f" (根据关键词'{keyword}'调整分类)"
        
        # 检查排除关键词
        exclusion_keywords = self.prompt_config.get('special_rules', {}).get('exclusion_keywords', {})
        current_category = classification_result.subcategory
        if current_category in exclusion_keywords:
            excluded_words = exclusion_keywords[current_category]
            for excluded_word in excluded_words:
                if excluded_word.lower() in text:
                    classification_result.confidence = max(classification_result.confidence - 0.3, 0.1)
                    classification_result.reasoning += f" (检测到排除关键词'{excluded_word}'，降低置信度)"
        
        return classification_result
    
    def _validate_classification(self, result: ClassificationResult) -> ClassificationResult:
        """验证分类结果"""
        thresholds = self.prompt_config.get('confidence_thresholds', {})
        
        if result.confidence < thresholds.get('low_confidence', 0.4):
            # 置信度过低，归类为Others
            result.subcategory = "Others"
            result.category = "rq2"
            result.reasoning += " (置信度过低，归类为Others)"
        
        return result