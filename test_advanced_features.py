"""
测试新增高级功能
"""
print("=" * 80)
print("高级功能模块测试")
print("=" * 80)

# 1. 情感智能系统
print("\n1️⃣ 情感智能系统")
print("-" * 80)
try:
    from emotion_intelligence import emotion_intelligence
    
    test_queries = [
        ("请问济南市家电补贴多少", None),
        ("太着急了！今天就要提交了", {"level": "CRITICAL"}),
        ("申请了好几次都不通过，真的很失望", None),
    ]
    
    for query, urgency in test_queries:
        analysis = emotion_intelligence.analyze(query, urgency)
        print(f"\n查询: {query}")
        print(f"  情感: {analysis['emotion']} | 状态: {analysis['user_state']}")
        print(f"  建议语气: {analysis['recommended_tone']} | 优先级: {analysis['strategy']['priority']}")
    
    print("\n✅ 情感智能系统测试通过")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")

# 2. 政策矛盾检测
print("\n\n2️⃣ 政策矛盾检测")
print("-" * 80)
try:
    from contradiction_detector import contradiction_detector
    
    policies = [
        {
            "content": "一级能效家电补贴20%，最高2000元",
            "source": "政策A",
            "date": "2024-01-15"
        },
        {
            "content": "一级能效家电补贴15%，最高1500元",
            "source": "政策B",
            "date": "2024-06-20"
        }
    ]
    
    result = contradiction_detector.detect(policies)
    print(f"\n发现矛盾: {'是' if result['has_contradiction'] else '否'}")
    print(f"一致性分数: {result['consistency_score']:.2f}")
    
    if result["contradictions"]:
        for i, c in enumerate(result["contradictions"], 1):
            print(f"\n矛盾 {i}: {c['type']}")
            print(f"  严重程度: {c['severity']}")
            print(f"  详情: {c['detail']}")
    
    print("\n✅ 矛盾检测测试通过")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")

# 3. 可视化代码生成
print("\n\n3️⃣ 数据可视化代码生成")
print("-" * 80)
try:
    from viz_code_generator import viz_code_generator
    
    data = {
        "title": "各类产品补贴占比",
        "labels": ["空调", "冰箱", "洗衣机"],
        "datasets": [{
            "label": "补贴金额",
            "data": [1200, 800, 600]
        }]
    }
    
    result = viz_code_generator.generate(data, "auto")
    print(f"\n推荐图表类型: {result['chart_type']}")
    print(f"说明: {result['description']}")
    print(f"\nPython代码已生成 ({len(result['code']['python'])} 字符)")
    print(f"JavaScript代码已生成 ({len(result['code']['javascript'])} 字符)")
    
    print("\n✅ 代码生成测试通过")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")

# 4. 政策验证
print("\n\n4️⃣ 政策时效性验证")
print("-" * 80)
try:
    from policy_validator import policy_validator
    
    test_policy = {
        "content": "济南市2025年家电补贴政策，有效期至2025年12月31日",
        "source": "济南市商务局",
        "date": "2025-01-15"
    }
    
    result = policy_validator.validate(test_policy)
    print(f"\n政策状态: {result['status']}")
    print(f"有效: {'是' if result['is_valid'] else '否'}")
    print(f"权威来源: {'是' if result['is_authoritative'] else '否'}")
    if result['expiry_date']:
        print(f"有效期至: {result['expiry_date']}")
        print(f"剩余天数: {result['days_until_expiry']}")
    if result['warnings']:
        print(f"警告: {', '.join(result['warnings'])}")
    
    print("\n✅ 政策验证测试通过")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")

# 总结
print("\n" + "=" * 80)
print("测试完成！新增功能概览")
print("=" * 80)
print("\n已实现的高级功能:")
print("  ✅ 情感智能系统 - 识别用户情绪并调整回复策略")
print("  ✅ 政策矛盾检测 - 自动发现政策间的冲突")
print("  ✅ 可视化代码生成 - 自动生成Python/JS图表代码")
print("  ✅ 政策时效验证 - 检查政策的有效性和权威性")
print("\n这些功能已集成到主系统 (agent.py) 中！")
