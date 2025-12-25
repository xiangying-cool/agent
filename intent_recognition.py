"""
双层意图识别系统
- 意图识别-1: 基础相关性判定（是否与政策相关）
- 意图识别-2: 任务路由（具体属于哪类需求）
"""
from typing import Dict, Tuple
import re
import config
from llm_client import LLMClient


class IntentRecognizer:
    """双层意图识别器"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.rejection_keywords = config.REJECTION_KEYWORDS
        
    def recognize(self, query: str) -> Dict:
        """
        执行双层意图识别
        
        Returns:
            {
                "is_relevant": bool,  # L1判定结果
                "intent_type": str,   # L2识别结果
                "confidence": float,  # 置信度
                "should_reject": bool, # 是否应拒绝
                "rejection_reason": str  # 拒绝原因
            }
        """
        # 第一层：相关性判定 + 安全检查
        is_relevant, rejection_info = self._level1_relevance_check(query)
        
        if not is_relevant:
            return {
                "is_relevant": False,
                "intent_type": None,
                "confidence": 0.0,
                "should_reject": True,
                "rejection_reason": rejection_info
            }
        
        # 第二层：任务路由
        intent_type, confidence = self._level2_task_routing(query)
        
        return {
            "is_relevant": True,
            "intent_type": intent_type,
            "confidence": confidence,
            "should_reject": False,
            "rejection_reason": None
        }
    
    def _level1_relevance_check(self, query: str) -> Tuple[bool, str]:
        """
        意图识别-1: 基础相关性判定
        
        Returns:
            (is_relevant, rejection_reason)
        """
        # 1. 安全检查 - 拒绝违规内容
        for keyword in self.rejection_keywords:
            if keyword in query:
                return False, f"检测到敏感内容，请咨询正规渠道"
        
        # 2. 关键词快速判断
        policy_keywords = [
            "以旧换新", "补贴", "换新", "家电", "数码", "汽车",
            "政策", "申请", "条件", "流程", "金额", "标准",
            "手机", "电视", "冰箱", "洗衣机", "空调", "平板"
        ]
        
        has_keyword = any(kw in query for kw in policy_keywords)
        
        # 3. 如果没有明显关键词，使用LLM判断
        if not has_keyword:
            is_relevant = self._llm_relevance_check(query)
            if not is_relevant:
                return False, "您的问题似乎与以旧换新政策无关，请询问政策相关问题"
        
        return True, None
    
    def _llm_relevance_check(self, query: str) -> bool:
        """使用LLM进行相关性判断"""
        prompt = f"""判断以下问题是否与"消费品以旧换新政策"相关。

问题：{query}

如果相关，回答"是"；如果不相关，回答"否"。
只需回答一个字。"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.chat(messages)
            return "是" in response
        except:
            # LLM调用失败时，保守策略：假设相关
            return True
    
    def _level2_task_routing(self, query: str) -> Tuple[str, float]:
        """
        意图识别-2: 任务路由
        
        Returns:
            (intent_type, confidence)
        """
        # 特征模式匹配
        patterns = {
            "CALCULATION": [
                r"补贴.*多少钱", r"能.*补.*多少", r"最[高多].*补贴",
                r"\d+元", r"计算", r"测算"
            ],
            "DATA_QUERY": [
                r"型号", r"品牌", r"参数", r"哪些.*可以",
                r"支持.*品牌", r"适用.*产品"
            ],
            "RECOMMENDATION": [
                r"推荐", r"建议", r"最[优好]", r"怎么.*划算",
                r"选.*还是", r"方案"
            ],
            "COMPLEX": [
                r"对比", r"区别", r"比较", r".*和.*有什么",
                r"跨.*", r"不同.*政策"
            ],
            "POLICY_QA": [
                r"补贴标准", r"标准", r"细则",
                r"如何.*申请", r"流程", r"条件", r"范围",
                r"什么.*时候", r"在哪", r"怎么.*办"
            ]
        }
        
        # 计算各类型匹配分数
        scores = {}
        for intent_type, pattern_list in patterns.items():
            score = 0
            for pattern in pattern_list:
                if re.search(pattern, query):
                    score += 1
            scores[intent_type] = score
        
        # 如果没有明显匹配，使用LLM判断
        if max(scores.values()) == 0:
            return self._llm_task_routing(query)
        
        # 返回得分最高的类型
        intent_type = max(scores, key=scores.get)
        confidence = min(scores[intent_type] * 0.3, 1.0)
        
        return intent_type, confidence
    
    def _llm_task_routing(self, query: str) -> Tuple[str, float]:
        """使用LLM进行任务路由"""
        intent_desc = "\n".join([
            f"{k}: {v}" for k, v in config.INTENT_TYPES.items()
        ])
        
        prompt = f"""请判断以下用户问题属于哪一类需求，只回答类型代码。

问题：{query}

类型选项：
{intent_desc}

请只回答类型代码（如：POLICY_QA），不要有其他内容。"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.chat(messages).strip()
            
            # 提取类型代码
            for intent_type in config.INTENT_TYPES.keys():
                if intent_type in response:
                    return intent_type, 0.7
            
            # 默认返回政策问答
            return "POLICY_QA", 0.5
        except:
            # LLM调用失败，默认返回政策问答
            return "POLICY_QA", 0.5


class RejectionHandler:
    """拒绝处理器 - 处理不合规或无关问题"""
    
    @staticmethod
    def get_rejection_response(reason: str) -> str:
        """生成拒绝回复"""
        templates = {
            "敏感内容": """抱歉，您的咨询涉及敏感内容，无法为您解答。

如需正规政策咨询，请：
1. 访问政府官方网站
2. 拨打政务服务热线 12345
3. 前往当地政务服务中心

感谢您的理解。""",
            
            "无关问题": """抱歉，您的问题似乎与"消费品以旧换新"政策无关。

我可以为您解答以下类型的问题：
✓ 家电、数码、汽车等产品的以旧换新补贴政策
✓ 补贴标准、申请流程、适用范围
✓ 具体产品型号的补贴金额
✓ 最优换新方案推荐

请重新描述您的政策咨询需求。"""
        }
        
        for key, template in templates.items():
            if key in reason:
                return template
        
        return f"""抱歉，暂时无法处理您的咨询。

原因：{reason}

如有疑问，请联系：
- 政务服务热线：12345
- 官方网站：[政府官网地址]

感谢您的理解。"""


if __name__ == "__main__":
    # 测试意图识别
    recognizer = IntentRecognizer()
    
    test_cases = [
        "济南市家电以旧换新补贴标准是多少？",
        "买iPhone 15能补贴多少钱？",
        "推荐一个最划算的家电换新方案",
        "济南和青岛的汽车补贴政策有什么区别？",
        "如何申请手机购新补贴？",
        "今天天气怎么样？",  # 无关问题
        "怎么钻政策漏洞？",  # 违规问题
    ]
    
    print("="*60)
    print("双层意图识别测试")
    print("="*60)
    
    for query in test_cases:
        print(f"\n问题: {query}")
        result = recognizer.recognize(query)
        
        if result["should_reject"]:
            print(f"❌ 拒绝处理")
            print(f"原因: {result['rejection_reason']}")
            rejection_response = RejectionHandler.get_rejection_response(
                result['rejection_reason']
            )
            print(f"\n回复:\n{rejection_response}")
        else:
            print(f"✓ 识别成功")
            print(f"类型: {result['intent_type']}")
            print(f"描述: {config.INTENT_TYPES.get(result['intent_type'])}")
            print(f"置信度: {result['confidence']:.2%}")
        
        print("-"*60)
