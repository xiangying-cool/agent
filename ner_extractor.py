"""
实体抽取模块 - 使用 LLM 提取关键实体
支持金额、产品类型、时间、地点等结构化信息提取
"""
from typing import Dict, List
from llm_client import LLMClient
import json
import re


class EntityExtractor:
    """实体抽取器"""
    
    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()
    
    def extract(self, query: str) -> Dict:
        """
        从用户问题中抽取实体
        
        Returns:
            {
                "amounts": [3000, 5000],  # 金额列表
                "products": ["冰箱", "手机"],  # 产品列表
                "locations": ["济南"],  # 地点列表
                "time_ranges": ["2024年"],  # 时间范围
                "actions": ["购买", "申请"],  # 动作
                "raw_entities": {...}  # 原始实体
            }
        """
        # 组合抽取：正则 + LLM
        regex_entities = self._regex_extract(query)
        llm_entities = self._llm_extract(query)
        
        # 合并结果（过滤无效产品名）
        valid_products = ["冰箱", "洗衣机", "电视", "空调", "热水器", 
                         "手机", "平板", "电脑", "笔记本", "手表",
                         "汽车", "新能源车", "燃油车"]
        
        all_products = regex_entities.get("products", []) + llm_entities.get("products", [])
        filtered_products = [p for p in all_products if p in valid_products]
        
        merged = {
            "amounts": list(set(regex_entities.get("amounts", []) + llm_entities.get("amounts", []))),
            "products": list(set(filtered_products)),
            "locations": llm_entities.get("locations", []),
            "time_ranges": llm_entities.get("time_ranges", []),
            "actions": llm_entities.get("actions", []),
            "raw_query": query
        }
        
        return merged
    
    def _regex_extract(self, query: str) -> Dict:
        """正则提取（快速但不够鲁棒）"""
        entities = {
            "amounts": [],
            "products": []
        }
        
        # 提取金额
        # 支持：3000元、3000块、3千、3k、3000-5000元
        amount_patterns = [
            r'(\d+)元',
            r'(\d+)块',
            r'(\d+)千',
            r'(\d+)[kK]',
            r'(\d+)-(\d+)',
            r'(\d+\.\d+)万'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                if isinstance(match, tuple):
                    for m in match:
                        if m:
                            try:
                                amount = float(m)
                                if '万' in pattern:
                                    amount *= 10000
                                elif '千' in pattern:
                                    amount *= 1000
                                entities["amounts"].append(int(amount))
                            except:
                                pass
                else:
                    try:
                        amount = float(match)
                        if '万' in pattern:
                            amount *= 10000
                        elif '千' in pattern:
                            amount *= 1000
                        entities["amounts"].append(int(amount))
                    except:
                        pass
        
        # 提取产品
        product_keywords = [
            "冰箱", "洗衣机", "电视", "空调", "热水器",
            "手机", "平板", "电脑", "笔记本", "手表",
            "汽车", "新能源车", "燃油车"
        ]
        
        for product in product_keywords:
            if product in query:
                entities["products"].append(product)
        
        return entities
    
    def _llm_extract(self, query: str) -> Dict:
        """LLM 提取（鲁棒但较慢）"""
        prompt = f"""请从以下问题中提取关键实体，以 JSON 格式返回。

问题：{query}

请提取：
- amounts: 金额列表（数字）
- products: 产品类型列表
- locations: 地点列表
- time_ranges: 时间范围列表
- actions: 用户动作（如"购买"、"申请"、"查询"等）

示例输入："我想在济南买3000元的冰箱，能补贴多少？"
示例输出：
{{
    "amounts": [3000],
    "products": ["冰箱"],
    "locations": ["济南"],
    "time_ranges": [],
    "actions": ["购买"]
}}

只返回 JSON，不要其他内容。"""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.chat(messages)
            
            # 提取 JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                entities = json.loads(json_match.group())
                return entities
        except Exception as e:
            print(f"LLM 实体抽取失败: {e}")
        
        return {
            "amounts": [],
            "products": [],
            "locations": [],
            "time_ranges": [],
            "actions": []
        }
    
    def build_structured_query(self, entities: Dict) -> Dict:
        """
        基于实体构建结构化查询
        
        Returns:
            {
                "query_type": "CALCULATION" | "SEARCH" | "RECOMMENDATION",
                "params": {...}
            }
        """
        amounts = entities.get("amounts", [])
        products = entities.get("products", [])
        actions = entities.get("actions", [])
        
        # 判断查询类型
        if amounts and ("购买" in actions or "补贴" in entities.get("raw_query", "")):
            # 补贴计算
            return {
                "query_type": "CALCULATION",
                "params": {
                    "amount": amounts[0] if amounts else 0,
                    "product": products[0] if products else "家电"
                }
            }
        elif "推荐" in actions or "方案" in entities.get("raw_query", ""):
            # 方案推荐
            return {
                "query_type": "RECOMMENDATION",
                "params": {
                    "budget": amounts[0] if amounts else 10000,
                    "needs": products
                }
            }
        else:
            # 政策查询
            return {
                "query_type": "SEARCH",
                "params": {
                    "keywords": products + entities.get("locations", [])
                }
            }


if __name__ == "__main__":
    # 测试实体抽取
    extractor = EntityExtractor()
    
    test_queries = [
        "我想在济南买3000元的冰箱，能补贴多少？",
        "手机购新补贴5000块的能补多少",
        "我有1万预算，推荐一个换新方案",
        "济南市家电以旧换新补贴标准是多少？"
    ]
    
    for query in test_queries:
        print(f"\n问题：{query}")
        entities = extractor.extract(query)
        print(f"实体：{json.dumps(entities, ensure_ascii=False, indent=2)}")
        
        structured = extractor.build_structured_query(entities)
        print(f"结构化查询：{json.dumps(structured, ensure_ascii=False, indent=2)}")
