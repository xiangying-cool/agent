"""
政策矛盾检测模块 - 检测多个政策之间的冲突和矛盾
"""
from typing import List, Dict, Tuple
import re
from datetime import datetime


class ContradictionDetector:
    """政策矛盾检测器"""
    
    def __init__(self):
        # 关键政策要素提取模式
        self.patterns = {
            "subsidy_rate": r'(\d+)%',  # 补贴比例
            "max_amount": r'最高(?:不超过)?(\d+)元',  # 最高金额
            "energy_level": r'([一二三四五]级)能效',  # 能效等级
            "date_range": r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # 日期
            "product_type": r'(家电|汽车|电动车|手机|电脑|空调|冰箱|洗衣机)',  # 产品类型
        }
    
    def detect(self, policies: List[Dict]) -> Dict:
        """
        检测政策间的矛盾
        
        Args:
            policies: 政策列表，每个包含 {content, source, date}
        
        Returns:
            {
                "has_contradiction": bool,
                "contradictions": [
                    {
                        "type": "矛盾类型",
                        "policy1": {...},
                        "policy2": {...},
                        "detail": "矛盾详情",
                        "severity": "HIGH/MEDIUM/LOW"
                    }
                ],
                "consistency_score": 0-1
            }
        """
        contradictions = []
        
        # 两两比较政策
        for i in range(len(policies)):
            for j in range(i + 1, len(policies)):
                conflicts = self._compare_policies(policies[i], policies[j])
                contradictions.extend(conflicts)
        
        # 计算一致性分数
        consistency_score = 1.0
        if contradictions:
            high_severity = sum(1 for c in contradictions if c["severity"] == "HIGH")
            medium_severity = sum(1 for c in contradictions if c["severity"] == "MEDIUM")
            consistency_score = max(0, 1.0 - (high_severity * 0.3 + medium_severity * 0.15))
        
        return {
            "has_contradiction": len(contradictions) > 0,
            "contradictions": contradictions,
            "consistency_score": consistency_score,
            "total_policies": len(policies)
        }
    
    def _compare_policies(self, policy1: Dict, policy2: Dict) -> List[Dict]:
        """比较两个政策"""
        conflicts = []
        
        text1 = policy1.get("content", "")
        text2 = policy2.get("content", "")
        
        # 1. 检查补贴比例矛盾
        rates1 = self._extract_subsidy_rates(text1)
        rates2 = self._extract_subsidy_rates(text2)
        
        if rates1 and rates2:
            # 相同产品不同补贴率
            conflict = self._check_rate_contradiction(rates1, rates2, policy1, policy2)
            if conflict:
                conflicts.append(conflict)
        
        # 2. 检查金额上限矛盾
        max1 = self._extract_max_amount(text1)
        max2 = self._extract_max_amount(text2)
        
        if max1 and max2 and abs(max1 - max2) > 500:  # 差异超过500元
            conflicts.append({
                "type": "金额上限不一致",
                "policy1": policy1,
                "policy2": policy2,
                "detail": f"政策1规定最高{max1}元，政策2规定最高{max2}元",
                "severity": "MEDIUM"
            })
        
        # 3. 检查时间冲突
        time_conflict = self._check_time_conflict(text1, text2, policy1, policy2)
        if time_conflict:
            conflicts.append(time_conflict)
        
        # 4. 检查互斥条件
        exclusive_conflict = self._check_exclusive_conditions(text1, text2, policy1, policy2)
        if exclusive_conflict:
            conflicts.append(exclusive_conflict)
        
        return conflicts
    
    def _extract_subsidy_rates(self, text: str) -> List[Tuple[str, int]]:
        """提取补贴比例"""
        results = []
        
        # 查找 "XX级能效 XX%"模式
        pattern = r'([一二三四五]级)能效.*?(\d+)%'
        matches = re.finditer(pattern, text)
        for match in matches:
            level = match.group(1)
            rate = int(match.group(2))
            results.append((level, rate))
        
        return results
    
    def _extract_max_amount(self, text: str) -> int:
        """提取最高金额"""
        match = re.search(self.patterns["max_amount"], text)
        if match:
            return int(match.group(1))
        return None
    
    def _check_rate_contradiction(self, rates1, rates2, policy1, policy2) -> Dict:
        """检查补贴率矛盾"""
        # 找出相同能效等级的不同补贴率
        rates1_dict = dict(rates1)
        rates2_dict = dict(rates2)
        
        for level in rates1_dict:
            if level in rates2_dict:
                rate1 = rates1_dict[level]
                rate2 = rates2_dict[level]
                if rate1 != rate2:
                    return {
                        "type": "补贴比例冲突",
                        "policy1": policy1,
                        "policy2": policy2,
                        "detail": f"{level}能效: 政策1为{rate1}%，政策2为{rate2}%",
                        "severity": "HIGH"
                    }
        return None
    
    def _check_time_conflict(self, text1, text2, policy1, policy2) -> Dict:
        """检查时间冲突"""
        # 检查是否有"废止"、"失效"等关键词
        if ("废止" in text1 or "失效" in text1) and policy1.get("source") == policy2.get("source"):
            return {
                "type": "政策时效冲突",
                "policy1": policy1,
                "policy2": policy2,
                "detail": "存在已废止政策与现行政策同时出现",
                "severity": "HIGH"
            }
        return None
    
    def _check_exclusive_conditions(self, text1, text2, policy1, policy2) -> Dict:
        """检查互斥条件"""
        # 检查是否有"仅限"、"只能"等互斥表述
        exclusive_words1 = ["仅限", "只能", "不得同时"]
        exclusive_words2 = ["可以同时", "允许叠加"]
        
        has_exclusive1 = any(word in text1 for word in exclusive_words1)
        has_inclusive2 = any(word in text2 for word in exclusive_words2)
        
        if has_exclusive1 and has_inclusive2:
            return {
                "type": "权益叠加规则冲突",
                "policy1": policy1,
                "policy2": policy2,
                "detail": "一个政策禁止叠加，另一个政策允许叠加",
                "severity": "MEDIUM"
            }
        return None
    
    def generate_resolution_advice(self, contradiction: Dict) -> str:
        """生成解决建议"""
        advice_map = {
            "补贴比例冲突": "建议以最新发布的政策为准，或咨询主管部门确认。",
            "金额上限不一致": "建议选择金额较高的政策申请，同时确认政策适用范围。",
            "政策时效冲突": "请以最新发布且未废止的政策为准。",
            "权益叠加规则冲突": "建议咨询政策发布部门，确认是否允许叠加享受补贴。"
        }
        
        c_type = contradiction.get("type", "")
        return advice_map.get(c_type, "建议咨询相关部门获取权威解释。")


# 全局实例
contradiction_detector = ContradictionDetector()


if __name__ == "__main__":
    # 测试矛盾检测
    detector = ContradictionDetector()
    
    print("=" * 60)
    print("政策矛盾检测测试")
    print("=" * 60)
    
    # 模拟政策数据
    test_policies = [
        {
            "content": "一级能效家电补贴20%，最高不超过2000元。有效期至2025年12月31日。",
            "source": "济南市政策A",
            "date": "2024-01-15"
        },
        {
            "content": "一级能效家电补贴15%，最高不超过1500元。仅限本市户籍居民申请。",
            "source": "济南市政策B",
            "date": "2024-06-20"
        },
        {
            "content": "二级能效家电补贴10%，最高不超过1000元。可以与其他优惠叠加享受。",
            "source": "省级政策C",
            "date": "2024-03-10"
        }
    ]
    
    result = detector.detect(test_policies)
    
    print(f"\n检测到矛盾: {'是' if result['has_contradiction'] else '否'}")
    print(f"一致性分数: {result['consistency_score']:.2f}")
    print(f"总政策数: {result['total_policies']}")
    
    if result["contradictions"]:
        print(f"\n发现 {len(result['contradictions'])} 个矛盾:")
        for i, contradiction in enumerate(result["contradictions"], 1):
            print(f"\n矛盾 {i}:")
            print(f"  类型: {contradiction['type']}")
            print(f"  严重程度: {contradiction['severity']}")
            print(f"  详情: {contradiction['detail']}")
            print(f"  政策1: {contradiction['policy1']['source']}")
            print(f"  政策2: {contradiction['policy2']['source']}")
            print(f"  解决建议: {detector.generate_resolution_advice(contradiction)}")
    
    print("\n✅ 矛盾检测测试完成")
