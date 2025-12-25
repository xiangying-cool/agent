"""
关键词提取插件 - 智能关键词提取
从文本中提取关键信息：实体、金额、日期、条件等
"""
from typing import Dict, Any, List
import re
from collections import Counter


class Plugin:
    """关键词提取插件"""
    
    @property
    def name(self) -> str:
        return "keyword_extractor"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "智能关键词提取：实体识别、金额提取、日期解析"
    
    def __init__(self):
        # 停用词
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', 
            '不', '人', '都', '一', '一个', '上', '也', '很',
            '到', '说', '要', '去', '你', '会', '着', '没有'
        }
        
        # 政策领域词汇
        self.domain_keywords = {
            '补贴', '政策', '申请', '条件', '标准', '流程',
            '家电', '汽车', '手机', '以旧换新', '购新',
            '补助', '奖励', '资助', '办理', '审核'
        }
    
    def on_load(self):
        print(f"[{self.name}] 关键词提取引擎已启动")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行关键词提取
        
        输入 context:
        {
            "text": "待提取文本",
            "extract_types": ["keywords", "amounts", "dates", "entities"],
            "top_k": 10  # 提取数量
        }
        
        输出:
        {
            "keywords": [...],
            "amounts": [...],
            "dates": [...],
            "entities": {...},
            "summary": "..."
        }
        """
        text = context.get("text", "")
        extract_types = context.get("extract_types", ["keywords", "amounts", "dates"])
        top_k = context.get("top_k", 10)
        
        if not text.strip():
            return {
                "keywords": [],
                "amounts": [],
                "dates": [],
                "entities": {},
                "summary": ""
            }
        
        result = {}
        
        # 提取关键词
        if "keywords" in extract_types:
            result["keywords"] = self._extract_keywords(text, top_k)
        
        # 提取金额
        if "amounts" in extract_types:
            result["amounts"] = self._extract_amounts(text)
        
        # 提取日期
        if "dates" in extract_types:
            result["dates"] = self._extract_dates(text)
        
        # 提取实体
        if "entities" in extract_types:
            result["entities"] = self._extract_entities(text)
        
        # 生成摘要
        result["summary"] = self._generate_summary(result, text)
        
        return result
    
    def _extract_keywords(self, text: str, top_k: int) -> List[Dict]:
        """提取关键词"""
        # 简单分词（中文按字符，实际应使用jieba）
        words = re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]+', text)
        
        # 过滤停用词
        words = [w for w in words if w not in self.stop_words and len(w) >= 2]
        
        # 统计词频
        word_freq = Counter(words)
        
        # 领域词汇加权
        for word in word_freq:
            if word in self.domain_keywords:
                word_freq[word] *= 2
        
        # 获取top_k
        top_words = word_freq.most_common(top_k)
        
        return [
            {
                "word": word,
                "frequency": freq,
                "importance": "high" if word in self.domain_keywords else "normal"
            }
            for word, freq in top_words
        ]
    
    def _extract_amounts(self, text: str) -> List[Dict]:
        """提取金额"""
        amounts = []
        
        # 匹配各种金额格式
        patterns = [
            (r'(\d+(?:\.\d+)?)元', '元'),
            (r'(\d+(?:\.\d+)?)%', '百分比'),
            (r'(\d+)万元', '万元'),
            (r'上限(\d+)', '上限'),
            (r'最高(\d+)', '最高')
        ]
        
        for pattern, amount_type in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                amounts.append({
                    "value": match.group(1),
                    "type": amount_type,
                    "context": text[max(0, match.start()-10):match.end()+10]
                })
        
        return amounts[:10]  # 最多返回10个
    
    def _extract_dates(self, text: str) -> List[Dict]:
        """提取日期"""
        dates = []
        
        # 匹配日期格式
        patterns = [
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', 'full_date'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', 'iso_date'),
            (r'(\d{4})年(\d{1,2})月', 'year_month'),
            (r'(\d{1,2})月(\d{1,2})日', 'month_day')
        ]
        
        for pattern, date_type in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                dates.append({
                    "date": match.group(0),
                    "type": date_type,
                    "position": match.start()
                })
        
        # 去重并排序
        seen = set()
        unique_dates = []
        for date in sorted(dates, key=lambda x: x["position"]):
            if date["date"] not in seen:
                seen.add(date["date"])
                unique_dates.append(date)
        
        return unique_dates[:10]
    
    def _extract_entities(self, text: str) -> Dict:
        """提取实体"""
        entities = {
            "products": [],
            "locations": [],
            "organizations": []
        }
        
        # 产品实体
        product_patterns = [
            '家电', '冰箱', '洗衣机', '空调', '电视',
            '手机', '平板', '汽车', '新能源汽车', '热水器'
        ]
        for product in product_patterns:
            if product in text:
                entities["products"].append(product)
        
        # 地点实体
        location_patterns = re.findall(r'([\u4e00-\u9fa5]{2,}(?:省|市|区|县))', text)
        entities["locations"] = list(set(location_patterns))[:5]
        
        # 组织机构实体
        org_patterns = re.findall(r'([\u4e00-\u9fa5]{2,}(?:局|部|委|厅|院))', text)
        entities["organizations"] = list(set(org_patterns))[:5]
        
        return entities
    
    def _generate_summary(self, extracted: Dict, original_text: str) -> str:
        """生成摘要"""
        summary_parts = []
        
        # 关键词摘要
        if "keywords" in extracted and extracted["keywords"]:
            top_3_keywords = [kw["word"] for kw in extracted["keywords"][:3]]
            summary_parts.append(f"核心关键词: {', '.join(top_3_keywords)}")
        
        # 金额摘要
        if "amounts" in extracted and extracted["amounts"]:
            amount_count = len(extracted["amounts"])
            summary_parts.append(f"提及{amount_count}处金额信息")
        
        # 日期摘要
        if "dates" in extracted and extracted["dates"]:
            date_count = len(extracted["dates"])
            summary_parts.append(f"包含{date_count}个时间节点")
        
        # 实体摘要
        if "entities" in extracted:
            entities = extracted["entities"]
            if entities.get("products"):
                summary_parts.append(f"涉及产品: {', '.join(entities['products'][:3])}")
        
        return "; ".join(summary_parts) if summary_parts else "未提取到关键信息"
