"""
紧急程度识别模块 - 识别用户问题的紧急程度
"""
from typing import Dict, Tuple
import re


class UrgencyDetector:
    """紧急程度识别器"""
    
    def __init__(self):
        # 紧急程度关键词
        self.urgent_keywords = {
            "CRITICAL": ["紧急", "马上", "立即", "赶快", "尽快", "着急", "快过期", "今天", "现在"],
            "HIGH": ["尽早", "早点", "快点", "希望快", "能否快", "时间不多", "明天"],
            "NORMAL": ["咨询", "了解", "请问", "想知道", "帮我", "查一下"],
        }
        
        # 时间敏感关键词
        self.time_sensitive = ["截止", "deadline", "最后", "期限", "过期", "失效"]
        
        # 情感强度词
        self.emotion_words = {
            "强烈": ["非常", "特别", "极其", "太", "超级", "一定要"],
            "中等": ["比较", "有点", "稍微", "还算"],
            "平淡": ["可能", "也许", "大概", "估计"]
        }
    
    def detect(self, query: str) -> Dict:
        """
        检测查询的紧急程度
        
        Args:
            query: 用户查询文本
        
        Returns:
            {
                "level": "CRITICAL/HIGH/NORMAL/LOW",
                "score": 0-100,
                "reasons": ["原因列表"],
                "priority": 1-4,  # 1最高
                "fast_track": True/False  # 是否开启快速通道
            }
        """
        score = 50  # 基础分数
        reasons = []
        level = "NORMAL"
        
        query_lower = query.lower()
        
        # 1. 检测紧急关键词
        for urgency_level, keywords in self.urgent_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    if urgency_level == "CRITICAL":
                        score += 30
                        reasons.append(f"包含紧急词'{keyword}'")
                        level = "CRITICAL"
                    elif urgency_level == "HIGH":
                        score += 15
                        reasons.append(f"包含优先词'{keyword}'")
                        if level == "NORMAL":
                            level = "HIGH"
        
        # 2. 检测时间敏感性
        for time_word in self.time_sensitive:
            if time_word in query:
                score += 20
                reasons.append(f"时间敏感'{time_word}'")
                if level == "NORMAL":
                    level = "HIGH"
        
        # 3. 检测情感强度
        for intensity, words in self.emotion_words.items():
            for word in words:
                if word in query:
                    if intensity == "强烈":
                        score += 10
                        reasons.append(f"情感强烈'{word}'")
                    break
        
        # 4. 检测问号数量（多问号表示着急）
        question_marks = query.count("?") + query.count("？")
        if question_marks >= 2:
            score += 10
            reasons.append(f"多个问号({question_marks}个)")
        
        # 5. 检测感叹号
        exclamation_marks = query.count("!") + query.count("！")
        if exclamation_marks >= 1:
            score += 5
            reasons.append(f"感叹号({exclamation_marks}个)")
        
        # 限制分数范围
        score = min(100, max(0, score))
        
        # 确定最终等级
        if score >= 80:
            level = "CRITICAL"
            priority = 1
        elif score >= 60:
            level = "HIGH"
            priority = 2
        elif score >= 40:
            level = "NORMAL"
            priority = 3
        else:
            level = "LOW"
            priority = 4
        
        # 是否开启快速通道
        fast_track = level in ["CRITICAL", "HIGH"]
        
        if not reasons:
            reasons = ["常规查询"]
        
        return {
            "level": level,
            "score": score,
            "reasons": reasons,
            "priority": priority,
            "fast_track": fast_track
        }
    
    def get_priority_queue_position(self, urgency_info: Dict, current_queue_length: int) -> int:
        """
        根据紧急程度计算在队列中的位置
        
        Args:
            urgency_info: detect() 返回的紧急度信息
            current_queue_length: 当前队列长度
        
        Returns:
            队列位置（0表示最前面）
        """
        priority = urgency_info["priority"]
        
        if priority == 1:  # CRITICAL
            return 0  # 插到最前面
        elif priority == 2:  # HIGH
            # 插到队列的前1/4位置
            return min(current_queue_length // 4, current_queue_length)
        else:
            # 正常排队
            return current_queue_length


# 全局实例
urgency_detector = UrgencyDetector()


if __name__ == "__main__":
    # 测试紧急程度识别
    detector = UrgencyDetector()
    
    print("=" * 60)
    print("紧急程度识别测试")
    print("=" * 60)
    
    test_queries = [
        "请问济南市家电补贴标准是多少",
        "紧急！今天就要提交申请，补贴怎么算？？",
        "马上要截止了，能否快点告诉我怎么办理",
        "非常着急！！尽快帮我查一下政策",
        "我想了解一下汽车以旧换新的政策",
        "明天deadline，请立即告诉我具体流程！"
    ]
    
    for query in test_queries:
        result = detector.detect(query)
        print(f"\n查询: {query}")
        print(f"  等级: {result['level']}")
        print(f"  评分: {result['score']}")
        print(f"  优先级: P{result['priority']}")
        print(f"  快速通道: {'是' if result['fast_track'] else '否'}")
        print(f"  原因: {', '.join(result['reasons'])}")
