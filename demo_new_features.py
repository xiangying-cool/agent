"""
新增功能演示 - 实际使用案例
"""
from agent import PolicyAgent
import time

print("=" * 80)
print("新增功能实际演示")
print("=" * 80)

# 初始化智能体
print("\n正在初始化智能体...")
agent = PolicyAgent(enable_advanced_features=True)
agent.initialize(force_rebuild=False)

# 测试案例
test_cases = [
    {
        "query": "请问济南市家电补贴标准是多少？",
        "description": "普通查询（无紧急标记）"
    },
    {
        "query": "紧急！今天就要提交申请，补贴怎么算？？",
        "description": "紧急查询（应该被标记为CRITICAL）"
    },
    {
        "query": "马上截止了，冰箱以旧换新能补贴多少钱",
        "description": "高优先级查询（时间敏感）"
    }
]

print("\n" + "=" * 80)
print("开始测试查询流程...")
print("=" * 80)

for i, case in enumerate(test_cases, 1):
    print(f"\n{'#' * 80}")
    print(f"测试案例 {i}: {case['description']}")
    print(f"问题: {case['query']}")
    print(f"{'#' * 80}\n")
    
    # 执行查询
    result = agent.query(case["query"], return_sources=True)
    
    # 显示结果摘要
    print(f"\n{'=' * 80}")
    print("结果摘要:")
    print(f"{'=' * 80}")
    print(f"意图类型: {result.get('intent_type', 'N/A')}")
    print(f"置信度: {result.get('confidence', 0):.2%}")
    
    # 显示紧急程度信息
    if 'urgency' in result:
        urgency = result['urgency']
        print(f"\n紧急程度:")
        print(f"  级别: {urgency['level']}")
        print(f"  评分: {urgency['score']}/100")
        print(f"  优先级: P{urgency['priority']}")
        print(f"  快速通道: {'是' if urgency['fast_track'] else '否'}")
        print(f"  原因: {', '.join(urgency['reasons'][:3])}")
    
    # 显示质量验证信息
    if 'quality_score' in result:
        print(f"\n质量评分:")
        print(f"  总分: {result['quality_score']}/100")
        print(f"  通过: {'是' if result.get('quality_passed', False) else '否'}")
    
    # 显示答案（截断）
    answer = result.get('answer', '')
    print(f"\n答案预览:")
    print(f"  {answer[:150]}..." if len(answer) > 150 else f"  {answer}")
    
    print(f"\n{'=' * 80}\n")
    
    time.sleep(1)  # 避免请求过快

# 查看监控统计
print("\n" + "=" * 80)
print("系统监控统计")
print("=" * 80)

if agent.monitoring_system:
    stats = agent.monitoring_system.get_statistics(minutes=60)
    print(f"\n最近60分钟统计:")
    print(f"  总请求数: {stats.get('total_requests', 0)}")
    print(f"  成功率: {stats.get('success_rate', 'N/A')}")
    print(f"  错误率: {stats.get('error_rate', 'N/A')}")
    print(f"  平均延迟: {stats.get('avg_latency_ms', 0):.2f}ms")
    print(f"  最大延迟: {stats.get('max_latency_ms', 0):.2f}ms")
    print(f"  平均置信度: {stats.get('avg_confidence', 'N/A')}")
    print(f"  系统状态: {stats.get('status', 'N/A')}")
    
    # 获取告警
    alerts = agent.monitoring_system.get_recent_alerts(5)
    if alerts:
        print(f"\n最近告警 ({len(alerts)}条):")
        for alert in alerts[:5]:
            print(f"  [{alert['level']}] {alert.get('message', alert.get('type', 'N/A'))}")
else:
    print("\n监控系统未启用")

# 模拟用户反馈
print("\n" + "=" * 80)
print("用户反馈收集演示")
print("=" * 80)

if agent.feedback_system:
    # 模拟一些反馈
    feedbacks = [
        {"rating": 5, "comment": "非常准确，帮助很大！"},
        {"rating": 4, "comment": "回答详细，但稍微有点慢"},
        {"rating": 3, "comment": "一般般"},
    ]
    
    print("\n收集用户反馈...")
    for i, fb in enumerate(feedbacks, 1):
        agent.feedback_system.collect_feedback(
            query=f"测试问题{i}",
            answer="测试回答...",
            rating=fb["rating"],
            comment=fb["comment"]
        )
    
    # 查看统计
    stats = agent.feedback_system.get_feedback_statistics()
    print(f"\n反馈统计:")
    print(f"  总反馈数: {stats.get('total_feedback', 0)}")
    print(f"  平均评分: {stats.get('average_rating', 0)}/5")
    print(f"  满意度: {stats.get('satisfaction_rate', 'N/A')}")
    
    # 获取改进建议
    suggestions = agent.feedback_system.get_improvement_suggestions()
    if suggestions:
        print(f"\n系统改进建议:")
        for i, sug in enumerate(suggestions[:3], 1):
            print(f"  {i}. {sug}")
else:
    print("\n反馈系统未启用")

print("\n" + "=" * 80)
print("演示完成！")
print("=" * 80)
print("\n新增功能已成功集成到系统中：")
print("  ✅ 紧急程度识别 - 自动识别并优先处理紧急查询")
print("  ✅ 质量验证 - 多维度验证答案质量，确保准确性")
print("  ✅ 性能监控 - 实时监控系统运行状态，自动告警")
print("  ✅ 反馈学习 - 收集用户反馈，持续改进系统")
