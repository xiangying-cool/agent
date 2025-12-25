"""
质量验证模块 - 多维度验证答案质量
"""
from typing import Dict, List
import re


class QualityValidator:
    """答案质量验证器"""
    
    def __init__(self):
        # 必要信息关键词
        self.required_elements = {
            "补贴": ["金额", "比例", "标准", "元", "%"],
            "流程": ["步骤", "第一", "第二", "首先", "然后", "最后"],
            "条件": ["需要", "要求", "必须", "应当"],
            "时间": ["日期", "时间", "期限", "截止", "年", "月", "日"]
        }
        
        # 数值格式检查
        self.number_patterns = {
            "金额": r"\d+\.?\d*元",
            "百分比": r"\d+\.?\d*%",
            "日期": r"\d{4}年\d{1,2}月\d{1,2}日"
        }
    
    def validate(self, question: str, answer: str, sources: List[Dict]) -> Dict:
        """
        全面验证答案质量
        
        Args:
            question: 用户问题
            answer: 系统答案
            sources: 参考来源列表
        
        Returns:
            验证报告
        """
        validation_result = {
            "overall_score": 0,
            "passed": False,
            "issues": [],
            "suggestions": [],
            "dimensions": {}
        }
        
        # 1. 准确性验证
        accuracy_score = self._check_accuracy(question, answer, sources)
        validation_result["dimensions"]["accuracy"] = accuracy_score
        
        # 2. 完整性验证
        completeness_score = self._check_completeness(question, answer)
        validation_result["dimensions"]["completeness"] = completeness_score
        
        # 3. 合规性验证
        compliance_score = self._check_compliance(answer)
        validation_result["dimensions"]["compliance"] = compliance_score
        
        # 4. 可读性验证
        readability_score = self._check_readability(answer)
        validation_result["dimensions"]["readability"] = readability_score
        
        # 计算总分
        overall_score = (
            accuracy_score["score"] * 0.4 +
            completeness_score["score"] * 0.3 +
            compliance_score["score"] * 0.2 +
            readability_score["score"] * 0.1
        )
        
        validation_result["overall_score"] = round(overall_score, 2)
        validation_result["passed"] = overall_score >= 70
        
        # 收集问题和建议
        for dimension in validation_result["dimensions"].values():
            validation_result["issues"].extend(dimension.get("issues", []))
            validation_result["suggestions"].extend(dimension.get("suggestions", []))
        
        return validation_result
    
    def _check_accuracy(self, question: str, answer: str, sources: List[Dict]) -> Dict:
        """检查准确性"""
        score = 100
        issues = []
        suggestions = []
        
        # 1. 检查是否有政策依据
        if not sources or len(sources) == 0:
            score -= 30
            issues.append("缺少政策依据来源")
            suggestions.append("添加参考来源")
        
        # 2. 检查数值准确性
        numbers_in_answer = re.findall(r'\d+\.?\d*', answer)
        if len(numbers_in_answer) > 0:
            # 检查是否有单位
            has_units = any(unit in answer for unit in ["元", "%", "件", "个", "天"])
            if not has_units:
                score -= 10
                issues.append("数值缺少单位")
                suggestions.append("为所有数值添加单位")
        
        # 3. 检查是否包含不确定表述
        uncertain_words = ["可能", "大概", "也许", "估计", "应该"]
        uncertain_count = sum(1 for word in uncertain_words if word in answer)
        if uncertain_count > 2:
            score -= 15
            issues.append(f"包含{uncertain_count}个不确定词汇")
            suggestions.append("使用更确定的表述")
        
        return {
            "score": max(0, score),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _check_completeness(self, question: str, answer: str) -> Dict:
        """检查完整性"""
        score = 100
        issues = []
        suggestions = []
        
        # 1. 识别问题类型并检查必要元素
        question_lower = question.lower()
        
        for topic, keywords in self.required_elements.items():
            if topic in question:
                # 检查答案是否包含必要元素
                found = sum(1 for kw in keywords if kw in answer)
                if found == 0:
                    score -= 25
                    issues.append(f"缺少'{topic}'相关必要信息")
                    suggestions.append(f"补充{keywords[0]}等信息")
                elif found < 2:
                    score -= 10
                    issues.append(f"'{topic}'信息不够详细")
        
        # 2. 检查答案长度
        if len(answer) < 50:
            score -= 20
            issues.append("答案过于简短")
            suggestions.append("扩充答案内容，提供更多细节")
        
        # 3. 检查结构化
        has_structure = any(marker in answer for marker in ["一、", "1.", "第一", "首先"])
        if not has_structure and len(answer) > 200:
            score -= 10
            issues.append("长答案缺少结构化")
            suggestions.append("使用序号或分点组织答案")
        
        return {
            "score": max(0, score),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _check_compliance(self, answer: str) -> Dict:
        """检查合规性"""
        score = 100
        issues = []
        suggestions = []
        
        # 1. 检查是否包含风险词汇
        risk_words = ["保证", "一定能", "百分百", "绝对", "肯定"]
        for word in risk_words:
            if word in answer:
                score -= 15
                issues.append(f"包含绝对化表述'{word}'")
                suggestions.append("使用更谨慎的表述")
        
        # 2. 检查是否有免责说明
        disclaimer_keywords = ["以官方", "最新", "实际", "咨询"]
        has_disclaimer = any(kw in answer for kw in disclaimer_keywords)
        if not has_disclaimer and len(answer) > 100:
            score -= 10
            issues.append("缺少免责或更新说明")
            suggestions.append("添加'以官方最新公告为准'等提示")
        
        # 3. 检查敏感词
        sensitive_words = ["违规", "作弊", "钻空子"]
        for word in sensitive_words:
            if word in answer:
                score -= 30
                issues.append(f"包含敏感词'{word}'")
                suggestions.append("移除不当表述")
        
        return {
            "score": max(0, score),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _check_readability(self, answer: str) -> Dict:
        """检查可读性"""
        score = 100
        issues = []
        suggestions = []
        
        # 1. 检查段落
        paragraphs = answer.split('\n\n')
        if len(paragraphs) == 1 and len(answer) > 300:
            score -= 15
            issues.append("长文本缺少分段")
            suggestions.append("使用段落分隔提高可读性")
        
        # 2. 检查重复
        sentences = [s.strip() for s in answer.split('。') if s.strip()]
        if len(sentences) > 1:
            # 简单检查是否有完全重复的句子
            if len(sentences) != len(set(sentences)):
                score -= 20
                issues.append("存在重复句子")
                suggestions.append("删除重复内容")
        
        # 3. 检查特殊符号使用
        emoji_count = len(re.findall(r'[📌🔔💡⚠️✓]', answer))
        if emoji_count > 10:
            score -= 10
            issues.append("表情符号过多")
            suggestions.append("适度使用表情符号")
        
        return {
            "score": max(0, score),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def auto_fix(self, answer: str, validation_result: Dict) -> str:
        """
        根据验证结果自动修正答案（简单版）
        
        Args:
            answer: 原始答案
            validation_result: 验证结果
        
        Returns:
            修正后的答案
        """
        fixed_answer = answer
        
        # 如果缺少免责说明，自动添加
        if any("免责" in issue for issue in validation_result["issues"]):
            if "注" not in fixed_answer[-100:]:
                fixed_answer += "\n\n注：以上信息基于现有政策文件，具体以官方最新公告为准。"
        
        # 如果有绝对化表述，添加提示
        risk_words = ["保证", "一定能", "百分百", "绝对", "肯定"]
        if any(word in fixed_answer for word in risk_words):
            if "提示" not in fixed_answer:
                fixed_answer += "\n\n提示：实际情况可能因具体条件而异，请以实际办理为准。"
        
        return fixed_answer


# 全局实例
quality_validator = QualityValidator()


if __name__ == "__main__":
    # 测试质量验证
    validator = QualityValidator()
    
    print("=" * 60)
    print("质量验证测试")
    print("=" * 60)
    
    test_cases = [
        {
            "question": "济南市家电补贴标准是多少",
            "answer": "补贴15%",
            "sources": []
        },
        {
            "question": "汽车以旧换新流程",
            "answer": "根据政策，汽车以旧换新补贴标准为：\n一、1级能效给予20%补贴\n二、2级能效给予15%补贴\n每件最高2000元。\n\n注：以官方最新公告为准。",
            "sources": [{"source": "政策文件.pdf"}]
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试案例{i}:")
        print(f"问题: {case['question']}")
        print(f"答案: {case['answer']}")
        
        result = validator.validate(
            case["question"],
            case["answer"],
            case["sources"]
        )
        
        print(f"\n总分: {result['overall_score']}/100")
        print(f"通过: {'是' if result['passed'] else '否'}")
        
        print("\n各维度评分:")
        for dim, data in result["dimensions"].items():
            print(f"  {dim}: {data['score']}")
        
        if result["issues"]:
            print("\n发现问题:")
            for issue in result["issues"]:
                print(f"  - {issue}")
        
        if result["suggestions"]:
            print("\n改进建议:")
            for sug in result["suggestions"]:
                print(f"  + {sug}")
