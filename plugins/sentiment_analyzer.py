"""
舆情分析插件 - 分析用户对产品的情感倾向
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugin_manager import PluginBase
from typing import Dict, Any
import random


class Plugin(PluginBase):
    """舆情分析插件"""
    
    @property
    def name(self) -> str:
        return "sentiment_analyzer"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "分析用户对产品的情感倾向，提供正面、负面、中性评价比例"
    
    def on_load(self):
        print("舆情分析插件初始化...")
        # 这里可以加载情感分析模型或初始化API客户端
        self.api_endpoint = "https://api.example.com/sentiment"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行情感分析
        
        Args:
            context: {
                "reviews": ["评论1", "评论2", ...],
                "product": "产品名称"
            }
        
        Returns:
            {
                "positive": 0.8,
                "negative": 0.1,
                "neutral": 0.1,
                "total_reviews": 100,
                "sample_reviews": ["正面评论示例", "负面评论示例"]
            }
        """
        reviews = context.get("reviews", [])
        product = context.get("product", "未知产品")
        
        # 如果没有提供评论，则生成模拟数据
        if not reviews:
            # 模拟情感分析结果
            positive = round(random.uniform(0.6, 0.9), 2)
            negative = round(random.uniform(0.05, 0.2), 2)
            neutral = round(1.0 - positive - negative, 2)
            
            # 确保数值有效
            if neutral < 0:
                neutral = 0.0
                remaining = 1.0 - negative
                positive = round(remaining, 2)
            
            total_reviews = random.randint(50, 500)
            
            # 生成示例评论
            sample_positive = f"{product}质量很好，性价比高，非常满意！"
            sample_negative = f"{product}使用体验一般，有些小问题。"
            sample_neutral = f"{product}还可以吧，没什么特别的。"
            
            return {
                "status": "success",
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "total_reviews": total_reviews,
                "sample_reviews": {
                    "positive": sample_positive,
                    "negative": sample_negative,
                    "neutral": sample_neutral
                },
                "product": product
            }
        
        # 如果提供了评论，则进行简单的情感分析
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        # 简单的关键词分析（实际应用中应使用NLP模型）
        positive_keywords = ["好", "棒", "优秀", "满意", "推荐", "赞", "喜欢", "不错"]
        negative_keywords = ["差", "坏", "垃圾", "失望", "问题", "糟糕", "不满", "缺陷"]
        
        for review in reviews:
            is_positive = any(keyword in review for keyword in positive_keywords)
            is_negative = any(keyword in review for keyword in negative_keywords)
            
            if is_positive and not is_negative:
                positive_count += 1
            elif is_negative and not is_positive:
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(reviews)
        positive_ratio = positive_count / total if total > 0 else 0.0
        negative_ratio = negative_count / total if total > 0 else 0.0
        neutral_ratio = neutral_count / total if total > 0 else 0.0
        
        # 选取示例评论
        sample_positive = next((r for r in reviews if any(kw in r for kw in positive_keywords)), "")
        sample_negative = next((r for r in reviews if any(kw in r for kw in negative_keywords)), "")
        sample_neutral = next((r for r in reviews if r not in [sample_positive, sample_negative]), "")
        
        return {
            "status": "success",
            "positive": round(positive_ratio, 2),
            "negative": round(negative_ratio, 2),
            "neutral": round(neutral_ratio, 2),
            "total_reviews": total,
            "sample_reviews": {
                "positive": sample_positive,
                "negative": sample_negative,
                "neutral": sample_neutral
            },
            "product": product
        }