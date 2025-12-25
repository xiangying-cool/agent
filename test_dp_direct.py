"""
直接测试推荐引擎（不依赖 LLM）
"""
from tools import RecommendationEngine

engine = RecommendationEngine()

print("="*80)
print("动态规划推荐算法测试")
print("="*80)

# 测试场景
test_budgets = [5000, 10000, 15000, 20000]

for budget in test_budgets:
    print(f"\n\n{'='*80}")
    print(f"预算：¥{budget}")
    print("="*80)
    
    # 贪心算法
    print("\n【贪心算法】")
    greedy = engine.recommend_max_subsidy_plan(budget, algorithm="greedy")
    if greedy.get('best_plan'):
        bp = greedy['best_plan']
        print(f"  推荐：{bp['product']} (¥{bp['price']})")
        print(f"  补贴：¥{bp['subsidy']}")
        print(f"  实付：¥{bp['net_cost']}")
    
    # 动态规划
    print("\n【动态规划（全局最优）】")
    dp = engine.recommend_max_subsidy_plan(budget, algorithm="dp")
    print(f"  选中：{len(dp['selected_products'])} 件")
    for p in dp['selected_products']:
        print(f"    • {p['name']} (¥{p['price']}) → 补贴¥{p['subsidy']}")
    print(f"  总价：¥{dp['total_price']}")
    print(f"  总补贴：¥{dp['total_subsidy']} ⭐")
    print(f"  实付：¥{dp['final_cost']}")
    print(f"  利用率：{dp['utilization_rate']:.1%}")
    
    # 对比
    greedy_subsidy = greedy.get('max_subsidy', 0) if greedy.get('best_plan') else 0
    improvement = dp['total_subsidy'] - greedy_subsidy
    improvement_pct = (improvement / max(greedy_subsidy, 1)) * 100
    
    print(f"\n【对比】")
    print(f"  补贴提升：¥{improvement} (+{improvement_pct:.1f}%)")
    print(f"  资金利用率：{dp['utilization_rate']:.1%}")

print("\n\n" + "="*80)
print("测试完成！")
print("="*80)
