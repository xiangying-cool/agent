"""
用户反馈学习系统 - 收集反馈并持续优化
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import config


class FeedbackSystem:
    """用户反馈收集与学习系统"""
    
    def __init__(self):
        self.feedback_dir = os.path.join(config.LOG_DIR, "feedback")
        self.feedback_file = os.path.join(self.feedback_dir, "feedback_data.json")
        self.optimization_file = os.path.join(self.feedback_dir, "optimizations.json")
        
        os.makedirs(self.feedback_dir, exist_ok=True)
        
        # 加载历史反馈
        self.feedback_history = self._load_feedback()
        self.optimizations = self._load_optimizations()
    
    def _load_feedback(self) -> List[Dict]:
        """加载历史反馈"""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _load_optimizations(self) -> Dict:
        """加载优化策略"""
        if os.path.exists(self.optimization_file):
            try:
                with open(self.optimization_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"strategies": [], "high_frequency_issues": []}
        return {"strategies": [], "high_frequency_issues": []}
    
    def collect_feedback(
        self,
        query: str,
        answer: str,
        rating: int,
        comment: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        收集用户反馈
        
        Args:
            query: 用户问题
            answer: 系统回答
            rating: 评分 1-5
            comment: 用户评论（可选）
            user_id: 用户ID（可选）
        
        Returns:
            反馈记录
        """
        feedback = {
            "id": len(self.feedback_history) + 1,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "answer": answer[:500],  # 限制长度
            "rating": rating,
            "comment": comment or "",
            "user_id": user_id or "anonymous",
            "processed": False
        }
        
        self.feedback_history.append(feedback)
        self._save_feedback()
        
        # 如果是负面反馈，立即分析
        if rating <= 2:
            self._analyze_negative_feedback(feedback)
        
        print(f"✓ 收到用户反馈: 评分 {rating}/5")
        return feedback
    
    def _save_feedback(self):
        """保存反馈数据"""
        try:
            with open(self.feedback_file, "w", encoding="utf-8") as f:
                json.dump(self.feedback_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存反馈失败: {e}")
    
    def _analyze_negative_feedback(self, feedback: Dict):
        """分析负面反馈"""
        issue = {
            "feedback_id": feedback["id"],
            "query": feedback["query"],
            "rating": feedback["rating"],
            "comment": feedback["comment"],
            "detected_at": datetime.now().isoformat()
        }
        
        # 检测问题类型
        comment_lower = feedback["comment"].lower()
        if any(word in comment_lower for word in ["不准", "错误", "不对"]):
            issue["type"] = "ACCURACY_ISSUE"
        elif any(word in comment_lower for word in ["不完整", "缺少", "没说"]):
            issue["type"] = "COMPLETENESS_ISSUE"
        elif any(word in comment_lower for word in ["慢", "等待", "超时"]):
            issue["type"] = "PERFORMANCE_ISSUE"
        else:
            issue["type"] = "OTHER"
        
        # 添加到高频问题列表
        self.optimizations["high_frequency_issues"].append(issue)
        self._save_optimizations()
        
        print(f"⚠️ 检测到负面反馈: {issue['type']}")
    
    def _save_optimizations(self):
        """保存优化策略"""
        try:
            with open(self.optimization_file, "w", encoding="utf-8") as f:
                json.dump(self.optimizations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存优化策略失败: {e}")
    
    def get_feedback_statistics(self) -> Dict:
        """获取反馈统计"""
        if not self.feedback_history:
            return {"message": "暂无反馈数据"}
        
        total = len(self.feedback_history)
        ratings = [f["rating"] for f in self.feedback_history]
        avg_rating = sum(ratings) / total
        
        rating_distribution = {
            "5星": sum(1 for r in ratings if r == 5),
            "4星": sum(1 for r in ratings if r == 4),
            "3星": sum(1 for r in ratings if r == 3),
            "2星": sum(1 for r in ratings if r == 2),
            "1星": sum(1 for r in ratings if r == 1)
        }
        
        satisfaction_rate = sum(1 for r in ratings if r >= 4) / total * 100
        
        return {
            "total_feedback": total,
            "average_rating": round(avg_rating, 2),
            "rating_distribution": rating_distribution,
            "satisfaction_rate": f"{satisfaction_rate:.2f}%",
            "negative_feedback_count": sum(1 for r in ratings if r <= 2)
        }
    
    def get_improvement_suggestions(self) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if not self.feedback_history:
            return ["暂无足够数据生成建议"]
        
        # 分析高频问题
        issues = self.optimizations.get("high_frequency_issues", [])
        if issues:
            issue_types = {}
            for issue in issues:
                issue_type = issue.get("type", "OTHER")
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            # 找出最常见的问题
            if issue_types:
                most_common = max(issue_types.items(), key=lambda x: x[1])
                if most_common[0] == "ACCURACY_ISSUE":
                    suggestions.append("建议: 加强知识库更新，提高答案准确性")
                elif most_common[0] == "COMPLETENESS_ISSUE":
                    suggestions.append("建议: 优化答案结构，补充更多细节信息")
                elif most_common[0] == "PERFORMANCE_ISSUE":
                    suggestions.append("建议: 优化检索算法，降低响应延迟")
        
        # 分析评分趋势
        recent_10 = self.feedback_history[-10:] if len(self.feedback_history) >= 10 else self.feedback_history
        avg_recent = sum(f["rating"] for f in recent_10) / len(recent_10)
        
        if avg_recent < 3.5:
            suggestions.append("警告: 最近评分偏低，需要紧急优化")
        
        if not suggestions:
            suggestions.append("系统运行良好，持续监控中")
        
        return suggestions
    
    def add_optimization_strategy(self, strategy: str, description: str):
        """添加优化策略"""
        opt = {
            "id": len(self.optimizations["strategies"]) + 1,
            "strategy": strategy,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.optimizations["strategies"].append(opt)
        self._save_optimizations()
        print(f"✓ 已添加优化策略: {strategy}")


# 全局反馈系统实例
feedback_system = FeedbackSystem()


if __name__ == "__main__":
    # 测试反馈系统
    fs = FeedbackSystem()
    
    print("=" * 60)
    print("反馈系统测试")
    print("=" * 60)
    
    # 模拟一些反馈
    test_feedbacks = [
        ("济南市家电补贴多少", "补贴标准为...", 5, "很准确！"),
        ("汽车以旧换新", "汽车补贴为...", 4, "不错"),
        ("电动车政策", "电动自行车...", 2, "回答不完整，缺少细节"),
        ("3C产品", "3C产品补贴...", 1, "答案不对，信息错误"),
        ("消费券", "消费券领取...", 5, "非常好用"),
    ]
    
    for query, answer, rating, comment in test_feedbacks:
        fs.collect_feedback(query, answer, rating, comment)
    
    # 查看统计
    print("\n反馈统计:")
    stats = fs.get_feedback_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 获取改进建议
    print("\n改进建议:")
    suggestions = fs.get_improvement_suggestions()
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
