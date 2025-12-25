"""
外部API管理器 - 集成多个外部数据源和服务
支持政策查询、价格查询等外部API
"""
from typing import Dict, List, Optional, Any
import requests
import time
from datetime import datetime, timedelta
import json

try:
    from external_api_config import EXTERNAL_API_CONFIG, get_api_headers
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("提示: external_api_config 未找到，使用默认配置")

try:
    from jd_api_helper import JDAPIHelper, parse_jd_response
    JD_HELPER_AVAILABLE = True
except ImportError:
    JD_HELPER_AVAILABLE = False
    print("提示: jd_api_helper 未找到，京东API签名不可用")


class ExternalAPIManager:
    """外部API管理器"""
    
    def __init__(self):
        # 使用外部配置文件或默认配置
        if CONFIG_AVAILABLE:
            # 从配置文件读取
            self.apis = {
                "price": {
                    "name": "价格比价API",
                    "base_url": EXTERNAL_API_CONFIG["price"]["base_url"],
                    "enabled": EXTERNAL_API_CONFIG["price"]["enabled"],
                    "timeout": EXTERNAL_API_CONFIG["price"]["timeout"],
                    "api_key": EXTERNAL_API_CONFIG["price"].get("api_key", "")
                },
                "policy_check": {
                    "name": "政策实时核查API",
                    "base_url": EXTERNAL_API_CONFIG["policy_check"]["base_url"],
                    "enabled": EXTERNAL_API_CONFIG["policy_check"]["enabled"],
                    "timeout": EXTERNAL_API_CONFIG["policy_check"]["timeout"],
                    "api_key": EXTERNAL_API_CONFIG["policy_check"].get("api_key", "")
                }
            }
        else:
            # 默认配置（未启用）
            self.apis = {
                "price": {
                    "name": "价格比价API",
                    "base_url": "https://api.jd.com/routerjson",
                    "enabled": False,
                    "timeout": 5,
                    "api_key": ""
                },
                "policy_check": {
                    "name": "政策实时核查API",
                    "base_url": "https://api.gov.cn/policy/check",
                    "enabled": False,
                    "timeout": 10,
                    "api_key": ""
                }
            }
        
        # 缓存配置
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存
        
        # 请求限流
        self.rate_limits = {}
        self.max_requests_per_minute = 60
        
        # 初始化京东API助手
        self.jd_helper = None
        if JD_HELPER_AVAILABLE and self.apis.get("price", {}).get("enabled"):
            app_key = self.apis["price"].get("app_key", "")
            app_secret = self.apis["price"].get("app_secret", "")
            if app_key and app_secret:
                self.jd_helper = JDAPIHelper(app_key, app_secret)
                print("✅ 京东API签名助手已初始化")
            else:
                print("⚠️ 京东API缺少app_secret，签名功能不可用")
    
    def call_api(
        self,
        api_name: str,
        endpoint: str = "",
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict:
        """
        调用外部API
        
        Args:
            api_name: API名称（weather/price/policy_check）
            endpoint: 端点路径
            method: 请求方法
            params: 查询参数
            data: 请求体数据
            use_cache: 是否使用缓存
        
        Returns:
            {
                "success": bool,
                "data": Any,
                "error": str,
                "cached": bool,
                "response_time": float
            }
        """
        start_time = time.time()
        
        # 检查API是否启用
        if api_name not in self.apis:
            return self._error_response(f"未知的API: {api_name}")
        
        api_config = self.apis[api_name]
        if not api_config["enabled"]:
            return self._mock_response(api_name, params)
        
        # 检查缓存
        cache_key = self._generate_cache_key(api_name, endpoint, params, data)
        if use_cache and cache_key in self.cache:
            cache_data, cache_time = self.cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return {
                    "success": True,
                    "data": cache_data,
                    "error": None,
                    "cached": True,
                    "response_time": time.time() - start_time
                }
        
        # 检查限流
        if not self._check_rate_limit(api_name):
            return self._error_response("请求频率超限，请稍后重试")
        
        # 构建URL
        url = api_config["base_url"]
        if endpoint:
            url = f"{url}/{endpoint}"
        
        # 初始化参数
        if params is None:
            params = {}
        
        # 获取请求头
        if CONFIG_AVAILABLE:
            headers = get_api_headers(api_name)
        else:
            headers = {"User-Agent": "IntelliPolicy/1.0"}
        
        try:
            # 发送请求
            if method.upper() == "GET":
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=api_config["timeout"]
                )
            elif method.upper() == "POST":
                response = requests.post(
                    url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=api_config["timeout"]
                )
            else:
                return self._error_response(f"不支持的请求方法: {method}")
            
            response.raise_for_status()
            
            # 解析响应
            result_data = response.json()
            
            # 缓存结果
            if use_cache:
                self.cache[cache_key] = (result_data, time.time())
            
            return {
                "success": True,
                "data": result_data,
                "error": None,
                "cached": False,
                "response_time": time.time() - start_time
            }
            
        except requests.exceptions.Timeout:
            return self._error_response("请求超时")
        except requests.exceptions.RequestException as e:
            return self._error_response(f"请求失败: {str(e)}")
        except json.JSONDecodeError:
            return self._error_response("响应数据格式错误")
    
    def check_policy_realtime(self, policy_name: str, region: str = "济南市") -> Dict:
        """
        实时核查政策状态
        
        Args:
            policy_name: 政策名称
            region: 地区
        
        Returns:
            {
                "policy_name": str,
                "status": "有效/已废止/已修订",
                "last_update": str,
                "source_url": str
            }
        """
        result = self.call_api(
            "policy_check",
            params={
                "name": policy_name,
                "region": region
            }
        )
        
        if result["success"] and result.get("data"):
            return result["data"]
        else:
            # 返回模拟数据
            return {
                "policy_name": policy_name,
                "region": region,
                "status": "有效",
                "last_update": datetime.now().strftime("%Y-%m-%d"),
                "source_url": "http://www.jinan.gov.cn/",
                "note": "实时核查服务暂不可用，返回本地数据"
            }
    
    def get_product_price(self, product_name: str, platform: str = "all") -> Dict:
        """
        获取商品价格
        
        Args:
            product_name: 商品名称
            platform: 平台（jd/tmall/all）
        
        Returns:
            {
                "product": str,
                "prices": [
                    {
                        "platform": str,
                        "price": float,
                        "url": str
                    }
                ],
                "lowest_price": float,
                "average_price": float
            }
        """
        # 如果有京东API助手，使用签名调用
        if self.jd_helper:
            try:
                # 构建京东查询参数
                jd_params = self.jd_helper.query_goods(
                    keyword=product_name,
                    page_index=1,
                    page_size=5
                )
                
                # 调用京东 API
                response = requests.post(
                    self.apis["price"]["base_url"],
                    data=jd_params,
                    timeout=self.apis["price"]["timeout"]
                )
                
                if response.status_code == 200:
                    jd_result = response.json()
                    parsed = parse_jd_response(jd_result)
                    
                    if parsed["success"] and parsed.get("data"):
                        # 解析京东数据格式
                        jd_data = parsed["data"]
                        goods_list = jd_data.get("data", [])
                        
                        if goods_list:
                            prices = []
                            for item in goods_list[:3]:  # 取前3个商品
                                price_info = {
                                    "platform": "京东",
                                    "price": float(item.get("price", 0) or item.get("wlUnitPrice", 0)),
                                    "name": item.get("skuName", product_name),
                                    "url": f"https://item.jd.com/{item.get('skuId', '')}.html" if item.get('skuId') else ""
                                }
                                prices.append(price_info)
                            
                            if prices:
                                price_values = [p["price"] for p in prices if p["price"] > 0]
                                return {
                                    "product": product_name,
                                    "prices": prices,
                                    "lowest_price": min(price_values) if price_values else 0,
                                    "average_price": sum(price_values) / len(price_values) if price_values else 0,
                                    "total_count": jd_data.get("totalCount", 0)
                                }
                    else:
                        print(f"京东API错误: {parsed.get('error', '未知')}")
            except Exception as e:
                print(f"京东API调用异常: {e}")
        
        # 如果京东API不可用或调用失败，返回模拟数据
        import random
        base_price = random.randint(2000, 8000)
        return {
            "product": product_name,
            "prices": [
                {
                    "platform": "京东",
                    "price": base_price,
                    "url": "https://www.jd.com"
                },
                {
                    "platform": "天猫",
                    "price": base_price * 0.95,
                    "url": "https://www.tmall.com"
                },
                {
                    "platform": "苏宁",
                    "price": base_price * 1.05,
                    "url": "https://www.suning.com"
                }
            ],
            "lowest_price": base_price * 0.95,
            "average_price": base_price,
            "note": "京东API不可用，返回模拟数据"
        }
    
    def batch_call(self, requests: List[Dict]) -> List[Dict]:
        """
        批量调用API
        
        Args:
            requests: [
                {
                    "api_name": str,
                    "endpoint": str,
                    "params": dict
                }
            ]
        
        Returns:
            响应列表
        """
        results = []
        for req in requests:
            result = self.call_api(
                req.get("api_name"),
                req.get("endpoint", ""),
                params=req.get("params")
            )
            results.append(result)
        return results
    
    def _generate_cache_key(self, api_name: str, endpoint: str, params: Dict, data: Dict) -> str:
        """生成缓存键"""
        key_parts = [api_name, endpoint or ""]
        if params:
            key_parts.append(json.dumps(params, sort_keys=True))
        if data:
            key_parts.append(json.dumps(data, sort_keys=True))
        return "|".join(key_parts)
    
    def _check_rate_limit(self, api_name: str) -> bool:
        """检查限流"""
        now = time.time()
        if api_name not in self.rate_limits:
            self.rate_limits[api_name] = []
        
        # 清理过期记录
        self.rate_limits[api_name] = [
            t for t in self.rate_limits[api_name]
            if now - t < 60
        ]
        
        # 检查是否超限
        if len(self.rate_limits[api_name]) >= self.max_requests_per_minute:
            return False
        
        # 记录本次请求
        self.rate_limits[api_name].append(now)
        return True
    
    def _error_response(self, error_msg: str) -> Dict:
        """错误响应"""
        return {
            "success": False,
            "data": None,
            "error": error_msg,
            "cached": False,
            "response_time": 0
        }
    
    def _mock_response(self, api_name: str, params: Optional[Dict]) -> Dict:
        """模拟响应（API未启用时）"""
        import random
        from datetime import datetime
        
        mock_data = {
            "price": {
                "product": params.get("product", "商品") if params else "商品",
                "prices": [{"platform": "京东", "price": 2999, "url": "https://jd.com"}],
                "lowest_price": 2999,
                "average_price": 2999
            },
            "policy_check": {
                "policy_name": params.get("name", "政策") if params else "政策",
                "region": params.get("region", "济南市") if params else "济南市",
                "status": "有效",
                "last_update": datetime.now().strftime("%Y-%m-%d"),
                "source_url": "http://www.jinan.gov.cn/"
            }
        }
        
        return {
            "success": True,
            "data": mock_data.get(api_name, {}),
            "error": None,
            "cached": False,
            "response_time": 0.1,
            "note": f"{self.apis[api_name]['name']}未启用，返回模拟数据"
        }
    
    def get_api_status(self) -> Dict:
        """获取所有API状态"""
        status = {}
        for api_name, config in self.apis.items():
            status[api_name] = {
                "name": config["name"],
                "enabled": config["enabled"],
                "cache_entries": sum(1 for k in self.cache if k.startswith(api_name)),
                "requests_last_minute": len(self.rate_limits.get(api_name, []))
            }
        return status
    
    def clear_cache(self, api_name: Optional[str] = None):
        """清空缓存"""
        if api_name:
            self.cache = {k: v for k, v in self.cache.items() if not k.startswith(api_name)}
        else:
            self.cache = {}


# 全局实例
external_api_manager = ExternalAPIManager()


if __name__ == "__main__":
    # 测试外部API管理器
    manager = ExternalAPIManager()
    
    print("=" * 60)
    print("外部API管理器测试")
    print("=" * 60)
    
    # 测试1: 政策核查
    print("\n1. 政策实时核查")
    print("-" * 60)
    result = manager.check_policy_realtime("济南市2025年家电补贴政策", "济南市")
    print(f"政策名称: {result['policy_name']}")
    print(f"状态: {result['status']}")
    print(f"最后更新: {result['last_update']}")
    if 'note' in result:
        print(f"注意: {result['note']}")
    
    # 测试2: 商品价格查询
    print("\n\n2. 商品价格查询")
    print("-" * 60)
    result = manager.get_product_price("海尔一级能效空调")
    if result.get('product'):
        print(f"商品: {result.get('product', 'N/A')}")
        print(f"平台价格:")
        for price_info in result.get('prices', []):
            print(f"  {price_info['platform']}: {price_info['price']:.2f}元")
        print(f"最低价: {result.get('lowest_price', 0):.2f}元")
        print(f"平均价: {result.get('average_price', 0):.2f}元")
    if 'note' in result:
        print(f"注意: {result['note']}")
    if not result.get('product'):
        print("⚠️ 京东 API 需要特殊的签名机制，当前返回空数据")
        print("请查看京东联盟 API 文档完成签名配置")
    
    # 测试3: 批量调用
    print("\n\n3. 批量API调用")
    print("-" * 60)
    batch_requests = [
        {"api_name": "price", "params": {"product": "冰箱"}},
        {"api_name": "policy_check", "params": {"name": "补贴政策"}},
    ]
    results = manager.batch_call(batch_requests)
    print(f"成功调用: {sum(1 for r in results if r['success'])}/{len(results)}")
    
    # 测试4: API状态
    print("\n\n4. API状态查询")
    print("-" * 60)
    status = manager.get_api_status()
    for api_name, info in status.items():
        print(f"\n{info['name']}:")
        print(f"  状态: {'启用' if info['enabled'] else '未启用（模拟模式）'}")
        print(f"  缓存条目: {info['cache_entries']}")
        print(f"  最近1分钟请求数: {info['requests_last_minute']}")
    
    print("\n\n✅ 外部API管理器测试完成")
