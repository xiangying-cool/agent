"""
查询优化插件 - 智能查询重写与扩展
提升检索准确率和召回率
"""
from typing import Dict, Any, List
import re


class Plugin:
    """查询优化插件"""
    
    @property
    def name(self) -> str:
        return "query_optimizer"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "智能查询重写、同义词扩展、关键词提取，提升检索效果"
    
    def __init__(self):
        # 同义词词典
        self.synonyms = {
            "补贴": ["补助", "资助", "奖励"],
            "申请": ["办理", "领取", "获取"],
            "流程": ["步骤", "程序", "手续"],
            "条件": ["要求", "标准", "资格"],
            "家电": ["电器", "家用电器"],
            "手机": ["移动电话", "智能手机"],
            "汽车": ["机动车", "小汽车", "车辆"],
        }
        
        # 停用词
        self.stop_words = {"的", "了", "吗", "呢", "啊", "吧", "是", "在"}
    
    def on_load(self):
        print(f"[{self.name}] 查询优化引擎已启动")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行查询优化
        
        输入 context:
        {
            "query": "原始查询",
            "max_expansions": 3  # 最多扩展数
        }
        
        输出:
        {
            "optimized_query": "优化后的查询",
            "expanded_queries": ["扩展查询1", "扩展查询2"],
            "keywords": ["关键词1", "关键词2"],
            "optimization_score": 0.85
        }
        """
        query = context.get("query", "")
        max_expansions = context.get("max_expansions", 3)
        
        if not query.strip():
            return {
                "optimized_query": query,
                "expanded_queries": [],
                "keywords": [],
                "optimization_score": 0.0
            }
        
        # 1. 提取关键词
        keywords = self._extract_keywords(query)
        
        # 2. 查询规范化
        normalized_query = self._normalize_query(query)
        
        # 3. 同义词扩展
        expanded_queries = self._expand_with_synonyms(normalized_query, max_expansions)
        
        # 4. 计算优化分数
        optimization_score = self._calculate_optimization_score(query, keywords, expanded_queries)
        
        return {
            "optimized_query": normalized_query,
            "expanded_queries": expanded_queries,
            "keywords": keywords,
            "optimization_score": optimization_score,
            "original_query": query
        }
    
    def _extract_keywords(self, query: str) -> List[str]:
        """提取关键词"""
        # 简单分词（生产环境建议使用jieba）
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', query)
        
        # 过滤停用词
        keywords = [w for w in words if w not in self.stop_words and len(w) > 1]
        
        return keywords[:5]  # 最多5个关键词
    
    def _normalize_query(self, query: str) -> str:
        """查询规范化"""
        # 去除多余空格
        normalized = ' '.join(query.split())
        
        # 统一标点符号
        normalized = normalized.replace('？', '?').replace('！', '!')
        
        # 去除无意义的疑问词
        normalized = re.sub(r'(请问|想问一下|咨询一下)', '', normalized)
        
        return normalized.strip()
    
    def _expand_with_synonyms(self, query: str, max_expansions: int) -> List[str]:
        """同义词扩展"""
        expanded = []
        
        for word, synonyms in self.synonyms.items():
            if word in query:
                for syn in synonyms[:max_expansions]:
                    expanded_query = query.replace(word, syn)
                    if expanded_query != query:
                        expanded.append(expanded_query)
                break  # 只扩展第一个匹配的词
        
        return expanded[:max_expansions]
    
    def _calculate_optimization_score(self, original: str, keywords: List[str], expanded: List[str]) -> float:
        """计算优化效果分数"""
        score = 0.0
        
        # 关键词数量
        score += min(len(keywords) / 5, 1.0) * 0.4
        
        # 扩展查询数量
        score += min(len(expanded) / 3, 1.0) * 0.3
        
        # 查询长度合理性（5-30字符）
        length_score = 1.0 if 5 <= len(original) <= 30 else 0.5
        score += length_score * 0.3
        
        return round(score, 2)
