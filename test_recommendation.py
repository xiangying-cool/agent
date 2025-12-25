"""测试推荐功能和图表数据"""
from agent import PolicyAgent

# 初始化智能体
print("正在初始化智能体...")
agent = PolicyAgent()
agent.initialize(force_rebuild=False)

# 测试查询
question = "我有15000元预算，推荐一个最划算的家电换新方案"
print(f"\n{'='*60}")
print(f"测试问题: {question}")
print(f"{'='*60}\n")

result = agent.query(question, return_sources=True)

print("\n" + "="*60)
print("返回结果分析")
print("="*60)

# 分析推荐数据
if 'recommendation' in result and result['recommendation']:
    rec = result['recommendation']
    print(f"\n✅ 推荐数据存在")
    print(f"   - 选中产品数: {len(rec.get('selected_products', []))}")
    print(f"   - 总补贴: ¥{rec.get('total_subsidy', 0)}")
    print(f"   - 实际花费: ¥{rec.get('final_cost', 0)}")
    print(f"   - 资金利用率: {rec.get('utilization_rate', 0):.1%}")
    
    print(f"\n📦 产品清单:")
    for i, p in enumerate(rec.get('selected_products', []), 1):
        print(f"   {i}. {p['name']} (¥{p['price']}) → 补贴¥{p['subsidy']}")
else:
    print("\n❌ 未找到推荐数据")

# 分析价格比较数据
if 'price_comparison' in result and result['price_comparison']:
    pc = result['price_comparison']
    print(f"\n✅ 价格比较数据存在")
    print(f"   - 状态: {pc.get('status')}")
    print(f"   - 总节省: ¥{pc.get('total_savings', 0)}")
    
    print(f"\n💰 价格对比:")
    for item in pc.get('comparisons', []):
        print(f"   {item['product']}: 京东¥{item['jd_price']} vs 淘宝¥{item['taobao_price']} (省¥{item['savings']})")
else:
    print("\n⚠️  未找到价格比较数据")

# 分析答案内容
print(f"\n📝 LLM 生成的答案（前500字）:")
print(result['answer'][:500] if result.get('answer') else "无答案")

print("\n" + "="*60)
print("图表数据验证")
print("="*60)

if 'recommendation' in result and result['recommendation']:
    rec = result['recommendation']
    
    # 验证图表所需数据
    print("\n✅ 柱状图数据:")
    for p in rec.get('selected_products', [])[:3]:  # 只显示前3个
        print(f"   - {p['name']}: 原价¥{p['price']}, 补贴¥{p['subsidy']}, 实付¥{p['price']-p['subsidy']}")
    
    print(f"\n✅ 饼图数据:")
    total = rec.get('total_subsidy', 1)
    for p in rec.get('selected_products', [])[:3]:
        percentage = (p['subsidy'] / total) * 100
        print(f"   - {p['name']}: {percentage:.1f}%")
    
    print(f"\n✅ 折线图数据:")
    print(f"   - 预算: ¥{rec.get('budget', 15000)}")
    print(f"   - 总花费: ¥{rec.get('total_cost', 0)}")
    print(f"   - 补贴后: ¥{rec.get('final_cost', 0)}")

print("\n" + "="*60)
print("测试完成！")
print("="*60)
