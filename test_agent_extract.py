import re

question = '我有20000元预算，推荐一个最划算的换新方案'
budgets = re.findall(r'(\d+)', question)
budget = float(budgets[0]) if budgets else 10000

needs = []
for product in ["冰箱", "洗衣机", "电视", "手机", "平板", "空调"]:
    if product in question:
        needs.append(product)

print(f'提取预算: {budget}')
print(f'提取需求: {needs}')
print(f'传入needs参数: {needs if needs else None}')

# 直接测试推荐引擎
from tools import RecommendationEngine
rec = RecommendationEngine()
result = rec.recommend_max_subsidy_plan(budget, needs if needs else None, algorithm="dp")
print(f'\n推荐结果:')
print(f'  - 选中产品数: {len(result["selected_products"])}')
print(f'  - 总补贴: {result["total_subsidy"]}')
