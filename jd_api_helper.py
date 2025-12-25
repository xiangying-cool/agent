"""
京东联盟API签名工具
实现京东API的签名机制和参数处理
"""
import hashlib
import time
import json
from typing import Dict, Any
from urllib.parse import quote


class JDAPIHelper:
    """京东联盟API辅助类"""
    
    def __init__(self, app_key: str, app_secret: str):
        """
        初始化京东API助手
        
        Args:
            app_key: 京东联盟AppKey
            app_secret: 京东联盟AppSecret (用于签名)
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.api_url = "https://api.jd.com/routerjson"
    
    def generate_sign(self, params: Dict[str, Any]) -> str:
        """
        生成京东API签名
        
        签名规则:
        1. 将所有参数(除sign外)按字母顺序排序
        2. 拼接成 key1value1key2value2... 格式
        3. 在开头和结尾加上app_secret
        4. 进行MD5加密
        5. 转换为大写
        
        Args:
            params: API参数字典
        
        Returns:
            签名字符串
        """
        # 过滤掉sign参数并排序
        sorted_params = sorted(
            [(k, v) for k, v in params.items() if k != 'sign' and v is not None],
            key=lambda x: x[0]
        )
        
        # 拼接字符串: secret + key1value1key2value2... + secret
        sign_str = self.app_secret
        for key, value in sorted_params:
            # 处理值，转换为字符串
            if isinstance(value, (dict, list)):
                value = json.dumps(value, separators=(',', ':'), ensure_ascii=False)
            else:
                value = str(value)
            sign_str += f"{key}{value}"
        sign_str += self.app_secret
        
        # MD5加密并转大写
        md5_hash = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        return md5_hash.upper()
    
    def build_request_params(
        self,
        method: str,
        param_json: Dict[str, Any],
        version: str = "1.0"
    ) -> Dict[str, Any]:
        """
        构建京东API请求参数
        
        Args:
            method: API方法名，如 "jd.union.open.goods.query"
            param_json: 业务参数
            version: API版本号
        
        Returns:
            完整的请求参数
        """
        # 基础参数
        params = {
            "app_key": self.app_key,
            "method": method,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "format": "json",
            "v": version,
            "sign_method": "md5",
        }
        
        # 添加业务参数(需要JSON序列化)
        if param_json:
            params["param_json"] = json.dumps(param_json, separators=(',', ':'), ensure_ascii=False)
        
        # 生成签名
        params["sign"] = self.generate_sign(params)
        
        return params
    
    def query_goods(
        self,
        keyword: str,
        page_index: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        查询商品信息
        
        Args:
            keyword: 搜索关键词
            page_index: 页码
            page_size: 每页数量
        
        Returns:
            请求参数
        """
        param_json = {
            "goodsReqDTO": {
                "keyword": keyword,
                "pageIndex": page_index,
                "pageSize": page_size,
            }
        }
        
        return self.build_request_params(
            method="jd.union.open.goods.query",
            param_json=param_json
        )
    
    def query_goods_promotiongoodsinfo(
        self,
        sku_ids: list
    ) -> Dict[str, Any]:
        """
        查询商品推广信息(含价格)
        
        Args:
            sku_ids: 商品SKU ID列表
        
        Returns:
            请求参数
        """
        param_json = {
            "skuIds": sku_ids
        }
        
        return self.build_request_params(
            method="jd.union.open.goods.promotiongoodsinfo.query",
            param_json=param_json
        )
    
    def get_material_goods(
        self,
        elite_id: int = 1,
        page_index: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        获取联盟推广商品
        
        Args:
            elite_id: 榜单ID (1-好券商品, 2-精选卖场等)
            page_index: 页码
            page_size: 每页数量
        
        Returns:
            请求参数
        """
        param_json = {
            "goodsReq": {
                "eliteId": elite_id,
                "pageIndex": page_index,
                "pageSize": page_size,
            }
        }
        
        return self.build_request_params(
            method="jd.union.open.goods.material.query",
            param_json=param_json
        )


def parse_jd_response(response_data: Dict) -> Dict:
    """
    解析京东API响应
    
    Args:
        response_data: 原始响应数据
    
    Returns:
        解析后的数据
    """
    # 京东API响应格式: {method_response: {code, data, message}}
    for key, value in response_data.items():
        if key.endswith('_response'):
            if isinstance(value, dict):
                # 检查是否成功
                if value.get('code') == '0' or 'result' in value:
                    return {
                        "success": True,
                        "data": value.get('result') or value.get('data'),
                        "message": value.get('message', '')
                    }
                else:
                    return {
                        "success": False,
                        "error": value.get('zh_desc') or value.get('message', '未知错误'),
                        "code": value.get('code')
                    }
    
    # 未找到响应
    return {
        "success": False,
        "error": "响应格式错误",
        "raw_response": response_data
    }


if __name__ == "__main__":
    # 测试签名生成
    print("=" * 60)
    print("京东联盟API签名测试")
    print("=" * 60)
    
    # 注意: 这里需要真实的AppKey和AppSecret
    # 从 https://union.jd.com/myTools/myApi 获取
    test_app_key = "your_app_key"
    test_app_secret = "your_app_secret"
    
    helper = JDAPIHelper(test_app_key, test_app_secret)
    
    # 测试1: 生成签名
    print("\n1. 签名生成测试")
    print("-" * 60)
    test_params = {
        "app_key": test_app_key,
        "method": "jd.union.open.goods.query",
        "timestamp": "2025-01-01 12:00:00",
        "format": "json",
        "v": "1.0",
        "sign_method": "md5",
        "param_json": '{"goodsReqDTO":{"keyword":"空调"}}'
    }
    sign = helper.generate_sign(test_params)
    print(f"生成的签名: {sign}")
    print(f"签名长度: {len(sign)} (应为32)")
    
    # 测试2: 构建完整请求参数
    print("\n\n2. 商品查询参数构建")
    print("-" * 60)
    query_params = helper.query_goods("海尔空调", page_index=1, page_size=5)
    print("请求参数:")
    for key, value in query_params.items():
        if key == "param_json":
            print(f"  {key}: {value[:50]}..." if len(value) > 50 else f"  {key}: {value}")
        else:
            print(f"  {key}: {value}")
    
    # 测试3: 解析响应示例
    print("\n\n3. 响应解析测试")
    print("-" * 60)
    
    # 成功响应示例
    success_response = {
        "jd_union_open_goods_query_response": {
            "code": "0",
            "result": {
                "data": [
                    {
                        "skuId": "123456",
                        "skuName": "测试商品",
                        "price": 2999.00
                    }
                ],
                "totalCount": 100
            }
        }
    }
    
    parsed = parse_jd_response(success_response)
    print(f"解析结果: {parsed}")
    
    # 错误响应示例
    error_response = {
        "jd_union_open_goods_query_response": {
            "code": "1001",
            "zh_desc": "参数错误"
        }
    }
    
    parsed_error = parse_jd_response(error_response)
    print(f"错误解析: {parsed_error}")
    
    print("\n" + "=" * 60)
    print("✅ 签名工具测试完成")
    print("\n💡 使用提示:")
    print("1. 需要在京东联盟后台获取 AppKey 和 AppSecret")
    print("2. AppSecret 用于签名，不要在代码中硬编码")
    print("3. 建议使用环境变量管理密钥")
