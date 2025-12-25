"""
情感智能系统 - 多维度情感分析与回复策略调整
整合情感识别、紧急程度、用户画像的智能系统
"""
from typing import Dict, Optional
import re


class EmotionIntelligence:
    """情感智能系统"""
    
    def __init__(self):
        # 情感关键词库
        self.emotion_keywords = {
            "anxious": ["着急", "焦虑", "担心", "紧张", "不安"],  # 焦虑
            "angry": ["生气", "愤怒", "不满", "恼火", "气愤"],  # 愤怒
            "confused": ["不懂", "不明白", "糊涂", "搞不清", "迷惑"],  # 困惑
            "disappointed": ["失望", "沮丧", "无奈", "遗憾"],  # 失望
            "satisfied": ["满意", "不错", "挺好", "可以", "感谢"],  # 满意
            "frustrated": ["烦", "麻烦", "复杂", "难办"],  # 受挫
        }
        
        # 情感状态与回复策略映射
        self.response_strategies = {
            "anxious": {
                "tone": "reassuring",  # 安抚性
                "prefix": "请放心，我来帮您快速解决。",
                "style": "简洁明了，突出重点",
                "priority": "HIGH"
            },
            "angry": {
                "tone": "apologetic",  # 歉意
                "prefix": "抱歉给您带来了困扰，让我立即为您核实。",
                "style": "诚恳，提供解决方案",
                "priority": "CRITICAL"
            },
            "confused": {
                "tone": "explanatory",  # 解释性
                "prefix": "我来为您详细说明。",
                "style": "分步骤，通俗易懂",
                "priority": "NORMAL"
            },
            "disappointed": {
                "tone": "empathetic",  # 共情
                "prefix": "理解您的心情，让我看看是否有其他办法。",
                "style": "提供替代方案",
                "priority": "HIGH"
            },
            "satisfied": {
                "tone": "positive",  # 积极
                "prefix": "很高兴能帮到您。",
                "style": "保持友好",
                "priority": "NORMAL"
            },
            "frustrated": {
                "tone": "supportive",  # 支持性
                "prefix": "我理解流程可能比较繁琐，让我帮您简化。",
                "style": "提供捷径和简化方案",
                "priority": "HIGH"
            },
            "neutral": {
                "tone": "professional",  # 专业
                "prefix": "",
                "style": "标准回复",
                "priority": "NORMAL"
            }
        }
    
    def analyze(self, query: str, urgency_info: Optional[Dict] = None) -> Dict:
        """
        综合分析用户情感和需求
        
        Args:
            query: 用户查询
            urgency_info: 紧急程度信息（来自urgency_detector）
        
        Returns:
            {
                "emotion": "情感类型",
                "emotion_score": 0-1,
                "strategy": {...回复策略},
                "user_state": "用户状态描述",
                "recommended_tone": "建议语气"
            }
        """
        # 检测情感
        emotion, emotion_score = self._detect_emotion(query)
        
        # 获取回复策略
        strategy = self.response_strategies.get(emotion, self.response_strategies["neutral"])
        
        # 结合紧急程度调整优先级
        if urgency_info and urgency_info.get("level") == "CRITICAL":
            strategy = strategy.copy()
            strategy["priority"] = "CRITICAL"
        
        # 用户状态分析
        user_state = self._analyze_user_state(emotion, urgency_info)
        
        return {
            "emotion": emotion,
            "emotion_score": emotion_score,
            "strategy": strategy,
            "user_state": user_state,
            "recommended_tone": strategy["tone"],
            "needs_empathy": emotion in ["angry", "disappointed", "frustrated"],
            "needs_simplification": emotion == "confused"
        }
    
    def _detect_emotion(self, text: str) -> tuple:
        """检测情感类型"""
        text_lower = text.lower()
        scores = {}
        
        # 计算每种情感的得分
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            if score > 0:
                scores[emotion] = score / len(keywords)  # 归一化
        
        if not scores:
            return "neutral", 0.5
        
        # 返回得分最高的情感
        dominant_emotion = max(scores.items(), key=lambda x: x[1])
        return dominant_emotion[0], min(dominant_emotion[1], 1.0)
    
    def _analyze_user_state(self, emotion: str, urgency_info: Optional[Dict]) -> str:
        """分析用户整体状态"""
        states = []
        
        # 情感状态
        emotion_desc = {
            "anxious": "焦虑状态",
            "angry": "情绪激动",
            "confused": "理解困难",
            "disappointed": "情绪低落",
            "satisfied": "满意状态",
            "frustrated": "感到受挫",
            "neutral": "平和状态"
        }
        states.append(emotion_desc.get(emotion, "正常"))
        
        # 紧急程度
        if urgency_info:
            level = urgency_info.get("level", "NORMAL")
            if level == "CRITICAL":
                states.append("高度紧急")
            elif level == "HIGH":
                states.append("较为紧急")
        
        return " + ".join(states)
    
    def adjust_response(self, original_response: str, emotion_analysis: Dict) -> str:
        """
        根据情感分析调整回复内容
        
        Args:
            original_response: 原始回复
            emotion_analysis: analyze()返回的情感分析结果
        
        Returns:
            调整后的回复
        """
        strategy = emotion_analysis["strategy"]
        prefix = strategy.get("prefix", "")
        
        # 如果需要共情
        if emotion_analysis.get("needs_empathy"):
            if prefix and not original_response.startswith(prefix):
                original_response = f"{prefix}\n\n{original_response}"
        
        # 如果用户困惑，添加分步说明标记
        if emotion_analysis.get("needs_simplification"):
            if "一、" not in original_response and "1." not in original_response:
                # 建议使用序号
                pass  # LLM会根据prompt自动调整
        
        # 添加情感标记到系统内部（不显示给用户）
        return original_response
    
    def generate_prompt_modifier(self, emotion_analysis: Dict) -> str:
        """
        生成prompt修饰语，用于指导LLM调整回复风格
        
        Returns:
            添加到system prompt的内容
        """
        strategy = emotion_analysis["strategy"]
        emotion = emotion_analysis["emotion"]
        
        modifiers = []
        
        # 基于情感的指导
        if emotion == "anxious":
            modifiers.append("用户较为焦虑，请使用简洁明了的语言，突出关键信息，给予确定性的答案。")
        elif emotion == "angry":
            modifiers.append("用户情绪激动，请先表示理解和歉意，然后快速给出解决方案。")
        elif emotion == "confused":
            modifiers.append("用户理解困难，请使用通俗语言，分步骤详细说明，避免专业术语。")
        elif emotion == "disappointed":
            modifiers.append("用户感到失望，请提供积极的替代方案，展示其他可能性。")
        elif emotion == "frustrated":
            modifiers.append("用户感到流程繁琐，请提供简化的办理路径，强调便捷性。")
        
        # 基于优先级的指导
        if strategy["priority"] == "CRITICAL":
            modifiers.append("这是紧急问题，请优先给出最核心的信息和立即可执行的步骤。")
        
        return " ".join(modifiers) if modifiers else ""


# 全局实例
emotion_intelligence = EmotionIntelligence()


if __name__ == "__main__":
    # 测试情感智能系统
    ei = EmotionIntelligence()
    
    print("=" * 60)
    print("情感智能系统测试")
    print("=" * 60)
    
    test_cases = [
        ("请问济南市家电补贴多少", None),
        ("太着急了！今天就要提交，怎么办？？", {"level": "CRITICAL"}),
        ("申请了好几次都不通过，真的很失望", None),
        ("这个流程太复杂了，我完全搞不懂", None),
        ("非常生气！为什么客服不回复？", None),
        ("谢谢，这个解释很清楚", None),
    ]
    
    for query, urgency in test_cases:
        print(f"\n查询: {query}")
        analysis = ei.analyze(query, urgency)
        
        print(f"  情感: {analysis['emotion']} (得分: {analysis['emotion_score']:.2f})")
        print(f"  用户状态: {analysis['user_state']}")
        print(f"  建议语气: {analysis['recommended_tone']}")
        print(f"  优先级: {analysis['strategy']['priority']}")
        print(f"  回复前缀: {analysis['strategy']['prefix']}")
        print(f"  Prompt指导: {ei.generate_prompt_modifier(analysis)[:60]}...")
    
    print("\n✅ 情感智能系统测试完成")
