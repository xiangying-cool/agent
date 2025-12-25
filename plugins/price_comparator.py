"""
价格比较插件 - 自动查询电商平台价格
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugin_manager import PluginBase
from typing import Dict, Any
import random
import time


class Plugin(PluginBase):
    """价格比较插件"""
    
    @property
    def name(self) -> str:
        return "price_comparator"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "自动查询京东、淘宝等电商平台价格，辅助用户决策"
    
    def on_load(self):
        print("价格比较插件初始化...")
        # 电商平台API端点（示例）
        self.api_endpoints = {
            "jd": "https://api.jd.com/price",
            "taobao": "https://api.taobao.com/price"
        }
        
        # 模拟API密钥（实际应用中应从配置文件或环境变量获取）
        self.api_keys = {
            "jd": "jd_api_key_placeholder",
            "taobao": "taobao_api_key_placeholder"
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行价格查询
        
        Args:
            context: {
                "products": ["冰箱", "洗衣机"],
                "budget": 10000
            }
        
        Returns:
            {
                "comparisons": [
                    {
                        "product": "冰箱",
                        "jd_price": 2999,
                        "taobao_price": 2899,
                        "best_platform": "taobao",
                        "savings": 100
                    }
                ]
            }
        """
        products = context.get("products", [])
        results = []
        
        for product in products:
            comparison = self._compare_prices(product)
            results.append(comparison)
        
        return {
            "status": "success",
            "comparisons": results,
            "total_savings": sum(c.get("savings", 0) for c in results)
        }
    
    def _compare_prices(self, product: str) -> Dict[str, Any]:
        """比较单个产品价格"""
        # 模拟API调用延迟
        time.sleep(0.1)
        
        # 生成模拟价格数据
        # 为了使价格看起来更真实，我们基于产品名称生成价格范围
        base_price = self._generate_base_price(product)
        
        # 生成各平台价格（有一定随机性）
        jd_price = round(base_price * random.uniform(0.95, 1.05), 2)
        taobao_price = round(base_price * random.uniform(0.90, 1.02), 2)
        
        # 确定最优平台和节省金额
        if jd_price < taobao_price:
            best_platform = "jd"
            savings = round(taobao_price - jd_price, 2)
        else:
            best_platform = "taobao"
            savings = round(jd_price - taobao_price, 2)
        
        return {
            "product": product,
            "jd_price": jd_price,
            "taobao_price": taobao_price,
            "best_platform": best_platform,
            "savings": savings,
            "url": f"https://search.{best_platform}.com/{product}"
        }
    
    def _generate_base_price(self, product: str) -> float:
        """根据产品名称生成基准价格"""
        # 简单的价格映射规则
        price_map = {
            "冰箱": 3000,
            "洗衣机": 2500,
            "电视": 4000,
            "空调": 3500,
            "手机": 3000,
            "平板": 2000
        }
        
        # 如果产品在映射中，使用映射价格
        for key, price in price_map.items():
            if key in product:
                return price * random.uniform(0.8, 1.2)
        
        # 默认价格
        return 2000 * random.uniform(0.5, 2.0)