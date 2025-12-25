"""
工具链模块 - 精确计算工具
解决大模型数值幻觉问题，所有数值计算由代码完成
"""
from typing import Dict, List, Tuple
import json
from datetime import datetime


class SubsidyCalculator:
    """补贴计算器 - 精确计算补贴金额"""
    
    def __init__(self):
        # 从表格知识库加载补贴规则
        self.rules = self._load_subsidy_rules()
    
    def _load_subsidy_rules(self) -> Dict:
        """加载补贴规则（实际应从数据库/文件加载）"""
        return {
            "家电": {
                "rate": 0.10,  # 10%补贴
                "max_per_item": 1000,  # 单台最高1000元
                "min_purchase": 500,  # 最低购买金额
                "categories": ["电视", "冰箱", "洗衣机", "空调", "热水器"]
            },
            "数码": {
                "手机": {"rate": 0.15, "max": 500, "min_purchase": 1000},
                "平板": {"rate": 0.15, "max": 300, "min_purchase": 800},
                "手表": {"rate": 0.10, "max": 200, "min_purchase": 500}
            },
            "汽车": {
                "燃油车": {"fixed": 10000, "condition": "报废旧车"},
                "新能源": {"fixed": 15000, "condition": "报废旧车"}
            }
        }
    
    def calculate_appliance_subsidy(self, 
                                   purchase_amount: float, 
                                   category: str = None) -> Dict:
        """
        计算家电补贴
        
        Args:
            purchase_amount: 购买金额
            category: 产品类别
            
        Returns:
            {
                "subsidy": 补贴金额,
                "calculation": 计算过程说明,
                "max_subsidy": 最高补贴,
                "actual_rate": 实际补贴率
            }
        """
        rules = self.rules["家电"]
        
        if purchase_amount < rules["min_purchase"]:
            return {
                "subsidy": 0,
                "calculation": f"购买金额¥{purchase_amount}未达到最低补贴标准¥{rules['min_purchase']}",
                "max_subsidy": 0,
                "actual_rate": 0
            }
        
        # 计算补贴金额
        calculated = purchase_amount * rules["rate"]
        subsidy = min(calculated, rules["max_per_item"])
        
        calculation = f"""
计算过程：
1. 购买金额：¥{purchase_amount}
2. 补贴比例：{rules['rate']*100}%
3. 理论补贴：¥{purchase_amount} × {rules['rate']*100}% = ¥{calculated:.2f}
4. 单台上限：¥{rules['max_per_item']}
5. 实际补贴：¥{subsidy:.2f}（取理论值与上限的较小值）
"""
        
        return {
            "subsidy": subsidy,
            "calculation": calculation.strip(),
            "max_subsidy": rules["max_per_item"],
            "actual_rate": subsidy / purchase_amount
        }
    
    def calculate_digital_subsidy(self, 
                                 product_type: str, 
                                 purchase_amount: float) -> Dict:
        """计算数码产品补贴"""
        if product_type not in self.rules["数码"]:
            return {
                "subsidy": 0,
                "calculation": f"产品类型'{product_type}'不在补贴范围内",
                "eligible": False
            }
        
        rules = self.rules["数码"][product_type]
        
        if purchase_amount < rules["min_purchase"]:
            return {
                "subsidy": 0,
                "calculation": f"购买金额¥{purchase_amount}未达到{product_type}最低标准¥{rules['min_purchase']}",
                "eligible": False
            }
        
        calculated = purchase_amount * rules["rate"]
        subsidy = min(calculated, rules["max"])
        
        return {
            "subsidy": subsidy,
            "calculation": f"{product_type}补贴：¥{purchase_amount} × {rules['rate']*100}% = ¥{calculated:.2f}，上限¥{rules['max']}，实际¥{subsidy}",
            "eligible": True,
            "max_subsidy": rules["max"]
        }
    
    def calculate_total_subsidy(self, shopping_list: List[Dict]) -> Dict:
        """
        计算多个商品的总补贴
        
        Args:
            shopping_list: [
                {"type": "家电", "category": "冰箱", "amount": 3000},
                {"type": "数码", "category": "手机", "amount": 5000}
            ]
        """
        total_subsidy = 0
        details = []
        
        for item in shopping_list:
            if item["type"] == "家电":
                result = self.calculate_appliance_subsidy(
                    item["amount"], 
                    item.get("category")
                )
            elif item["type"] == "数码":
                result = self.calculate_digital_subsidy(
                    item["category"],
                    item["amount"]
                )
            else:
                continue
            
            total_subsidy += result.get("subsidy", 0)
            details.append({
                "item": item,
                "subsidy": result.get("subsidy", 0),
                "calculation": result.get("calculation")
            })
        
        return {
            "total_subsidy": total_subsidy,
            "items_count": len(shopping_list),
            "details": details,
            "summary": f"共{len(shopping_list)}件商品，总补贴¥{total_subsidy:.2f}"
        }


class RecommendationEngine:
    """智能推荐引擎 - 推荐最优换新方案"""
    
    def __init__(self):
        self.calculator = SubsidyCalculator()
    
    def recommend_max_subsidy_plan(self, 
                                  budget: float,
                                  needs: List[str] = None,
                                  algorithm: str = "dp") -> Dict:
        """
        推荐补贴最大化方案
        
        Args:
            budget: 总预算
            needs: 需求列表，如 ["冰箱", "洗衣机", "手机"]
            algorithm: 算法类型 - "greedy"（贪心）或 "dp"（动态规划，默认）
        
        Returns:
            {
                "selected_products": [{"name": "冰箱", "price": 3000, "subsidy": 300}, ...],
                "total_price": 9500,
                "total_subsidy": 1050,
                "final_cost": 8450,
                "utilization_rate": 0.633,
                "algorithm_used": "dp",
                "is_optimal": True
            }
        """
        if algorithm == "dp":
            return self._recommend_dp(budget, needs)
        else:
            return self._recommend_greedy(budget, needs)
    
    def _recommend_dp(self, budget: float, needs: List[str] = None) -> Dict:
        """
        动态规划算法（全局最优）- 0-1背包问题
        优化目标：在预算内使补贴总额最大
        性能优化: 滚动数组 + 稀疏状态
        """
        # 定义产品库(优化:减少产品数量)
        products = [
            {"name": "冰箱", "price": 2000, "type": "家电"},
            {"name": "冰箱", "price": 3500, "type": "家电"},
            {"name": "冰箱", "price": 6000, "type": "家电"},
            {"name": "洗衣机", "price": 1500, "type": "家电"},
            {"name": "洗衣机", "price": 2500, "type": "家电"},
            {"name": "电视", "price": 3000, "type": "家电"},
            {"name": "电视", "price": 5000, "type": "家电"},
            {"name": "空调", "price": 2500, "type": "家电"},
            {"name": "空调", "price": 4000, "type": "家电"},
            {"name": "手机", "price": 2000, "type": "数码", "category": "手机"},
            {"name": "手机", "price": 4000, "type": "数码", "category": "手机"},
            {"name": "平板", "price": 1500, "type": "数码", "category": "平板"},
            {"name": "平板", "price": 2500, "type": "数码", "category": "平板"},
        ]
        
        # 根据需求过滤
        if needs:
            products = [p for p in products if p["name"] in needs]
        
        if not products:
            return {"selected_products": [], "total_price": 0, "total_subsidy": 0, 
                    "final_cost": 0, "utilization_rate": 0, "algorithm_used": "dp", 
                    "is_optimal": True, "message": "无可用产品"}
        
        # 计算每个产品的补贴
        for product in products:
            if product["type"] == "家电":
                result = self.calculator.calculate_appliance_subsidy(product["price"])
            else:
                result = self.calculator.calculate_digital_subsidy(
                    product.get("category", "手机"), product["price"]
                )
            product["subsidy"] = result.get("subsidy", 0)
        
        # 动态规划(优化:滚动数组,空间O(W))
        n = len(products)
        W = int(budget)
        
        # 使用一维滚动数组
        dp = [0] * (W + 1)
        parent = [[] for _ in range(W + 1)]  # 记录选中的产品索引
        
        for i in range(n):
            price = int(products[i]["price"])
            subsidy = int(products[i]["subsidy"])
            
            # 从后往前遍历(避免重复选择)
            for w in range(W, price - 1, -1):
                if dp[w - price] + subsidy > dp[w]:
                    dp[w] = dp[w - price] + subsidy
                    parent[w] = parent[w - price] + [i]
        
        # 提取选中的产品
        selected_indices = parent[W]
        selected = [products[i] for i in selected_indices]
        
        total_price = sum(p["price"] for p in selected)
        total_subsidy = sum(p["subsidy"] for p in selected)
        final_cost = total_price - total_subsidy
        utilization_rate = total_price / budget if budget > 0 else 0
        
        return {
            "selected_products": selected,
            "total_price": total_price,
            "total_subsidy": total_subsidy,
            "final_cost": final_cost,
            "utilization_rate": utilization_rate,
            "algorithm_used": "dp",
            "is_optimal": True,
            "max_possible_subsidy": dp[W]
        }
    
    def _recommend_greedy(self, budget: float, needs: List[str] = None) -> Dict:
        """
        贪心算法（原有逻辑，保留作为对比）
        """
        # 预定义常见产品及价格区间
        products = {
            "电视": [3000, 5000, 8000],
            "冰箱": [2000, 3500, 6000],
            "洗衣机": [1500, 2500, 4000],
            "空调": [2500, 4000, 6000],
            "手机": [2000, 4000, 6000],
            "平板": [1500, 2500, 4000]
        }
        
        # 如果用户指定需求，只考虑这些产品
        if needs:
            products = {k: v for k, v in products.items() if k in needs}
        
        best_plan = None
        max_subsidy = 0
        
        # 枚举组合（简化版，实际可用动态规划优化）
        for product, prices in products.items():
            for price in prices:
                if price <= budget:
                    # 判断产品类型
                    if product in ["电视", "冰箱", "洗衣机", "空调"]:
                        result = self.calculator.calculate_appliance_subsidy(price, product)
                    elif product == "手机":
                        result = self.calculator.calculate_digital_subsidy("手机", price)
                    elif product == "平板":
                        result = self.calculator.calculate_digital_subsidy("平板", price)
                    else:
                        continue
                    
                    if result["subsidy"] > max_subsidy:
                        max_subsidy = result["subsidy"]
                        best_plan = {
                            "product": product,
                            "price": price,
                            "subsidy": result["subsidy"],
                            "net_cost": price - result["subsidy"]
                        }
        
        return {
            "best_plan": best_plan,
            "max_subsidy": max_subsidy,
            "budget": budget,
            "recommendation": f"推荐购买{best_plan['product']}（¥{best_plan['price']}），可获补贴¥{best_plan['subsidy']}，实付¥{best_plan['net_cost']}",
            "algorithm_used": "greedy",
            "is_optimal": False
        }
    
    def recommend_multi_item_plan(self,
                                 budget: float,
                                 max_items: int = 3) -> Dict:
        """推荐多商品组合方案"""
        # 简化实现：贪心算法选择性价比最高的组合
        products = [
            {"name": "冰箱", "type": "家电", "price": 3000, "priority": 1},
            {"name": "洗衣机", "type": "家电", "price": 2500, "priority": 2},
            {"name": "电视", "type": "家电", "price": 4000, "priority": 3},
            {"name": "手机", "type": "数码", "category": "手机", "price": 4000, "priority": 1},
        ]
        
        # 按性价比排序
        selected = []
        remaining_budget = budget
        
        for product in sorted(products, key=lambda x: x["priority"]):
            if len(selected) >= max_items:
                break
            
            if product["price"] <= remaining_budget:
                if product["type"] == "家电":
                    result = self.calculator.calculate_appliance_subsidy(
                        product["price"], 
                        product["name"]
                    )
                else:
                    result = self.calculator.calculate_digital_subsidy(
                        product["category"],
                        product["price"]
                    )
                
                selected.append({
                    "product": product["name"],
                    "price": product["price"],
                    "subsidy": result["subsidy"]
                })
                remaining_budget -= product["price"]
        
        total_price = sum(item["price"] for item in selected)
        total_subsidy = sum(item["subsidy"] for item in selected)
        
        return {
            "plan": selected,
            "total_items": len(selected),
            "total_price": total_price,
            "total_subsidy": total_subsidy,
            "net_cost": total_price - total_subsidy,
            "remaining_budget": remaining_budget
        }


class PolicyValidator:
    """政策验证器 - 验证是否符合政策条件"""
    
    @staticmethod
    def validate_time_range(policy_start: str, 
                          policy_end: str) -> Tuple[bool, str]:
        """验证当前时间是否在政策有效期内"""
        try:
            start = datetime.strptime(policy_start, "%Y-%m-%d")
            end = datetime.strptime(policy_end, "%Y-%m-%d")
            now = datetime.now()
            
            if now < start:
                return False, f"政策尚未开始（开始时间：{policy_start}）"
            elif now > end:
                return False, f"政策已结束（结束时间：{policy_end}）"
            else:
                days_left = (end - now).days
                return True, f"政策有效中（剩余{days_left}天）"
        except:
            return True, "无法验证时间范围"
    
    @staticmethod
    def validate_eligibility(conditions: Dict, 
                           user_info: Dict) -> Tuple[bool, List[str]]:
        """验证用户是否符合申请条件"""
        unmet_conditions = []
        
        for key, required_value in conditions.items():
            user_value = user_info.get(key)
            if user_value != required_value:
                unmet_conditions.append(f"{key}: 需要{required_value}，当前{user_value}")
        
        is_eligible = len(unmet_conditions) == 0
        return is_eligible, unmet_conditions


if __name__ == "__main__":
    # 测试补贴计算
    print("="*60)
    print("工具链测试 - 补贴计算")
    print("="*60)
    
    calculator = SubsidyCalculator()
    
    # 测试1: 家电补贴
    print("\n【测试1】家电补贴计算")
    result = calculator.calculate_appliance_subsidy(3000, "冰箱")
    print(f"补贴金额: ¥{result['subsidy']}")
    print(result['calculation'])
    
    # 测试2: 数码补贴
    print("\n【测试2】手机补贴计算")
    result = calculator.calculate_digital_subsidy("手机", 5000)
    print(f"补贴金额: ¥{result['subsidy']}")
    print(result['calculation'])
    
    # 测试3: 总补贴计算
    print("\n【测试3】购物清单总补贴")
    shopping_list = [
        {"type": "家电", "category": "冰箱", "amount": 3000},
        {"type": "家电", "category": "洗衣机", "amount": 2500},
        {"type": "数码", "category": "手机", "amount": 5000}
    ]
    result = calculator.calculate_total_subsidy(shopping_list)
    print(f"总补贴: ¥{result['total_subsidy']}")
    print(result['summary'])
    
    # 测试4: 智能推荐（动态规划）
    print("\n【测试4】智能推荐（动态规划）")
    engine = RecommendationEngine()
    result = engine.recommend_max_subsidy_plan(5000, ["冰箱", "手机"], algorithm="dp")
    print(f"选中产品：{len(result['selected_products'])}件")
    for p in result['selected_products']:
        print(f"  - {p['name']}（¥{p['price']}）→ 补贴¥{p['subsidy']}")
    print(f"总补贴：¥{result['total_subsidy']}，实付：¥{result['final_cost']}")
    print(f"资金利用率：{result['utilization_rate']:.1%}")
    
    # 测试5：对比贪心 vs 动态规划
    print("\n【测试5】算法对比：贪心 vs 动态规划")
    budget = 15000
    print(f"预算：¥{budget}，无限制")
    
    # 贪心算法
    result_greedy = engine.recommend_max_subsidy_plan(budget, algorithm="greedy")
    print(f"贪心算法：")
    if 'best_plan' in result_greedy and result_greedy['best_plan']:
        bp = result_greedy['best_plan']
        print(f"  - 推荐：{bp['product']}（¥{bp['price']}）")
        print(f"  - 补贴：¥{bp['subsidy']}，实付：¥{bp['net_cost']}")
    
    # 动态规划
    result_dp = engine.recommend_max_subsidy_plan(budget, algorithm="dp")
    print(f"动态规划（全局最优）：")
    print(f"  - 选中：{len(result_dp['selected_products'])}件")
    for p in result_dp['selected_products']:
        print(f"    • {p['name']}（¥{p['price']}）→ 补贴¥{p['subsidy']}")
    print(f"  - 总价：¥{result_dp['total_price']}，总补贴：¥{result_dp['total_subsidy']}，实付：¥{result_dp['final_cost']}")
    print(f"  - 资金利用率：{result_dp['utilization_rate']:.1%}")
    
    greedy_subsidy = result_greedy.get('max_subsidy', 0) if result_greedy.get('best_plan') else 0
    dp_subsidy = result_dp['total_subsidy']
    print(f"对比结果：")
    print(f"  - 补贴差异：¥{dp_subsidy - greedy_subsidy} (动态规划提升 {((dp_subsidy - greedy_subsidy)/max(greedy_subsidy, 1)*100):.1f}%)")
    
    print("\n" + "="*60)
