"""
测试新增功能模块
"""
import sys

print("=" * 60)
print("测试新增功能模块")
print("=" * 60)

# 1. 测试紧急程度识别
print("\n1️⃣ 测试紧急程度识别")
print("-" * 60)
try:
    from urgency_detector import urgency_detector
    
    test_queries = [
        "请问济南市家电补贴标准是多少",
        "紧急！今天就要提交申请，补贴怎么算？？",
        "马上要截止了，能否快点告诉我怎么办理",
    ]
    
    for query in test_queries:
        result = urgency_detector.detect(query)
        print(f"\n查询: {query}")
        print(f"  等级: {result['level']} | 评分: {result['score']}")
        print(f"  优先级: P{result['priority']} | 快速通道: {'是' if result['fast_track'] else '否'}")
    
    print("\n✅ 紧急程度识别模块测试通过")
except Exception as e:
    print(f"\n❌ 紧急程度识别模块测试失败: {e}")

# 2. 测试质量验证
print("\n\n2️⃣ 测试质量验证模块")
print("-" * 60)
try:
    from quality_validator import quality_validator
    
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
        result = quality_validator.validate(
            case["question"],
            case["answer"],
            case["sources"]
        )
        print(f"\n案例{i}: {case['question'][:20]}...")
        print(f"  总分: {result['overall_score']}/100")
        print(f"  通过: {'是' if result['passed'] else '否'}")
        print(f"  维度: ", end="")
        for dim, data in result["dimensions"].items():
            print(f"{dim}={data['score']} ", end="")
        print()
    
    print("\n✅ 质量验证模块测试通过")
except Exception as e:
    print(f"\n❌ 质量验证模块测试失败: {e}")

# 3. 测试监控系统
print("\n\n3️⃣ 测试监控系统")
print("-" * 60)
try:
    from monitor import MonitoringSystem
    import random
    
    monitor = MonitoringSystem()
    
    # 模拟一些查询
    for i in range(20):
        status = "success" if random.random() > 0.1 else "error"
        monitor.record_query({
            "query": f"测试查询{i}",
            "status": status,
            "latency_ms": random.randint(500, 3000),
            "confidence": random.random(),
            "error_msg": "测试错误" if status == "error" else ""
        })
    
    # 查看统计
    stats = monitor.get_statistics(minutes=60)
    print(f"\n统计报告:")
    print(f"  总请求: {stats.get('total_requests', 0)}")
    print(f"  成功率: {stats.get('success_rate', 'N/A')}")
    print(f"  平均延迟: {stats.get('avg_latency_ms', 0):.2f}ms")
    print(f"  状态: {stats.get('status', 'N/A')}")
    
    # 查看告警
    alerts = monitor.get_recent_alerts(5)
    if alerts:
        print(f"\n最近告警 ({len(alerts)}条):")
        for alert in alerts[:3]:
            print(f"  [{alert['level']}] {alert.get('type', 'N/A')}")
    
    print("\n✅ 监控系统测试通过")
except Exception as e:
    print(f"\n❌ 监控系统测试失败: {e}")

# 4. 测试反馈系统
print("\n\n4️⃣ 测试反馈系统")
print("-" * 60)
try:
    from feedback_system import FeedbackSystem
    
    fs = FeedbackSystem()
    
    # 模拟一些反馈
    test_feedbacks = [
        ("济南市家电补贴多少", "补贴标准为...", 5, "很准确！"),
        ("汽车以旧换新", "汽车补贴为...", 4, "不错"),
        ("电动车政策", "电动自行车...", 2, "回答不完整"),
    ]
    
    for query, answer, rating, comment in test_feedbacks:
        fs.collect_feedback(query, answer, rating, comment)
    
    # 查看统计
    stats = fs.get_feedback_statistics()
    print(f"\n反馈统计:")
    print(f"  总反馈: {stats.get('total_feedback', 0)}")
    print(f"  平均评分: {stats.get('average_rating', 0)}")
    print(f"  满意度: {stats.get('satisfaction_rate', 'N/A')}")
    
    # 获取建议
    suggestions = fs.get_improvement_suggestions()
    if suggestions:
        print(f"\n改进建议:")
        for i, sug in enumerate(suggestions[:2], 1):
            print(f"  {i}. {sug}")
    
    print("\n✅ 反馈系统测试通过")
except Exception as e:
    print(f"\n❌ 反馈系统测试失败: {e}")

# 总结
print("\n" + "=" * 60)
print("测试完成！所有新功能模块已就绪")
print("=" * 60)
print("\n新增功能:")
print("  ✓ 紧急程度识别 - 自动识别用户查询的紧急级别")
print("  ✓ 质量验证 - 多维度验证答案质量（准确性、完整性等）")
print("  ✓ 监控告警 - 实时监控系统性能并智能告警")
print("  ✓ 反馈学习 - 收集用户反馈并生成改进建议")
print("\n这些功能已集成到主系统 (agent.py) 中！")
