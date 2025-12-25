"""
政策对比插件 - 智能政策对比分析
支持多个政策文件的差异对比、版本演进分析
"""
from typing import Dict, Any, List
import re
from difflib import SequenceMatcher


class Plugin:
    """政策对比插件"""
    
    @property
    def name(self) -> str:
        return "policy_comparator"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "智能政策对比：差异分析、版本演进、条款变更追踪"
    
    def on_load(self):
        print(f"[{self.name}] 政策对比引擎已启动")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行政策对比
        
        输入 context:
        {
            "policies": [
                {"name": "政策A", "content": "...", "date": "2024-01-01"},
                {"name": "政策B", "content": "...", "date": "2025-01-01"}
            ],
            "comparison_type": "full|key_changes|summary"
        }
        
        输出:
        {
            "comparison_result": {...},
            "similarity_score": 0.85,
            "key_differences": [...],
            "recommendations": [...]
        }
        """
        policies = context.get("policies", [])
        comparison_type = context.get("comparison_type", "summary")
        
        if len(policies) < 2:
            return {
                "error": "至少需要2个政策进行对比",
                "comparison_result": {},
                "similarity_score": 0.0,
                "key_differences": [],
                "recommendations": []
            }
        
        # 只对比前两个政策
        policy_a = policies[0]
        policy_b = policies[1]
        
        # 计算相似度
        similarity_score = self._calculate_similarity(
            policy_a.get("content", ""),
            policy_b.get("content", "")
        )
        
        # 提取关键差异
        key_differences = self._extract_key_differences(policy_a, policy_b)
        
        # 生成对比结果
        if comparison_type == "full":
            comparison_result = self._full_comparison(policy_a, policy_b)
        elif comparison_type == "key_changes":
            comparison_result = self._key_changes_comparison(policy_a, policy_b)
        else:  # summary
            comparison_result = self._summary_comparison(policy_a, policy_b, similarity_score)
        
        # 生成建议
        recommendations = self._generate_recommendations(policy_a, policy_b, key_differences)
        
        return {
            "comparison_result": comparison_result,
            "similarity_score": round(similarity_score, 3),
            "key_differences": key_differences,
            "recommendations": recommendations,
            "policy_count": len(policies)
        }
    
    def _calculate_similarity(self, text_a: str, text_b: str) -> float:
        """计算文本相似度"""
        if not text_a or not text_b:
            return 0.0
        
        # 使用 SequenceMatcher 计算相似度
        matcher = SequenceMatcher(None, text_a, text_b)
        return matcher.ratio()
    
    def _extract_key_differences(self, policy_a: Dict, policy_b: Dict) -> List[Dict]:
        """提取关键差异"""
        differences = []
        
        # 提取金额差异
        amounts_a = self._extract_amounts(policy_a.get("content", ""))
        amounts_b = self._extract_amounts(policy_b.get("content", ""))
        
        if amounts_a != amounts_b:
            differences.append({
                "type": "金额变更",
                "before": amounts_a,
                "after": amounts_b,
                "impact": "high"
            })
        
        # 提取日期差异
        dates_a = self._extract_dates(policy_a.get("content", ""))
        dates_b = self._extract_dates(policy_b.get("content", ""))
        
        if dates_a != dates_b:
            differences.append({
                "type": "时间范围变更",
                "before": dates_a,
                "after": dates_b,
                "impact": "medium"
            })
        
        # 提取条件差异
        conditions_a = self._extract_conditions(policy_a.get("content", ""))
        conditions_b = self._extract_conditions(policy_b.get("content", ""))
        
        new_conditions = set(conditions_b) - set(conditions_a)
        removed_conditions = set(conditions_a) - set(conditions_b)
        
        if new_conditions:
            differences.append({
                "type": "新增条件",
                "items": list(new_conditions),
                "impact": "high"
            })
        
        if removed_conditions:
            differences.append({
                "type": "移除条件",
                "items": list(removed_conditions),
                "impact": "medium"
            })
        
        return differences
    
    def _extract_amounts(self, text: str) -> List[str]:
        """提取金额"""
        # 匹配金额模式：数字+元
        amounts = re.findall(r'\d+(?:\.\d+)?元', text)
        return list(set(amounts))[:5]  # 去重，最多5个
    
    def _extract_dates(self, text: str) -> List[str]:
        """提取日期"""
        # 匹配日期模式
        dates = re.findall(r'\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}', text)
        return list(set(dates))[:5]
    
    def _extract_conditions(self, text: str) -> List[str]:
        """提取条件"""
        # 简单提取包含"条件"、"要求"、"需"等关键词的句子
        conditions = []
        sentences = re.split(r'[。！？]', text)
        
        for sentence in sentences:
            if any(kw in sentence for kw in ['条件', '要求', '需', '必须', '应当']):
                conditions.append(sentence.strip())
        
        return conditions[:5]
    
    def _full_comparison(self, policy_a: Dict, policy_b: Dict) -> Dict:
        """完整对比"""
        return {
            "policy_a": {
                "name": policy_a.get("name"),
                "date": policy_a.get("date"),
                "length": len(policy_a.get("content", ""))
            },
            "policy_b": {
                "name": policy_b.get("name"),
                "date": policy_b.get("date"),
                "length": len(policy_b.get("content", ""))
            },
            "comparison_type": "完整对比"
        }
    
    def _key_changes_comparison(self, policy_a: Dict, policy_b: Dict) -> Dict:
        """关键变更对比"""
        return {
            "title": f"{policy_a.get('name')} vs {policy_b.get('name')}",
            "focus": "关键变更点",
            "comparison_type": "关键变更对比"
        }
    
    def _summary_comparison(self, policy_a: Dict, policy_b: Dict, similarity: float) -> Dict:
        """摘要对比"""
        if similarity > 0.8:
            conclusion = "两个政策高度相似，仅有微小调整"
        elif similarity > 0.5:
            conclusion = "政策有一定变化，建议关注差异部分"
        else:
            conclusion = "政策变化较大，建议详细对比"
        
        return {
            "policy_a_name": policy_a.get("name"),
            "policy_b_name": policy_b.get("name"),
            "similarity": similarity,
            "conclusion": conclusion,
            "comparison_type": "摘要对比"
        }
    
    def _generate_recommendations(self, policy_a: Dict, policy_b: Dict, differences: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if not differences:
            recommendations.append("两个政策基本一致，无需特别关注")
            return recommendations
        
        for diff in differences:
            if diff.get("impact") == "high":
                recommendations.append(f"重点关注：{diff.get('type')}")
            elif diff.get("type") == "新增条件":
                recommendations.append("注意新增的申请条件，可能影响资格审核")
            elif diff.get("type") == "金额变更":
                recommendations.append("补贴金额有调整，建议重新计算预期收益")
        
        return recommendations[:5]  # 最多5条建议
