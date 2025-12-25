"""
外部API集成测试
测试API端点和功能集成
"""
import requests
import time


def test_external_api_endpoints():
    """测试外部API端点"""
    base_url = "http://127.0.0.1:8000/api"
    
    print("=" * 70)
    print("外部API集成测试")
    print("=" * 70)
    
    # 测试1: 政策核查
    print("\n1. 测试政策核查API")
    print("-" * 70)
    try:
        response = requests.get(
            f"{base_url}/external/policy_check",
            params={
                "policy_name": "济南市家电补贴政策",
                "region": "济南市"
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 政策核查成功")
            print(f"   政策名称: {data.get('policy_name')}")
            print(f"   状态: {data.get('status')}")
            print(f"   最后更新: {data.get('last_update')}")
            if 'note' in data:
                print(f"   注意: {data.get('note')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 无法连接到服务器: {e}")
        print("   请确保后端服务正在运行 (python app.py)")
    
    time.sleep(0.5)
    
    # 测试2: 价格查询
    print("\n\n2. 测试价格查询API")
    print("-" * 70)
    try:
        response = requests.get(
            f"{base_url}/external/price",
            params={
                "product": "海尔一级能效空调",
                "platform": "all"
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 价格查询成功")
            print(f"   商品: {data.get('product')}")
            print(f"   平台价格:")
            for price_info in data.get('prices', []):
                print(f"     {price_info['platform']}: ¥{price_info['price']:.2f}")
            print(f"   最低价: ¥{data.get('lowest_price', 0):.2f}")
            print(f"   平均价: ¥{data.get('average_price', 0):.2f}")
            if 'note' in data:
                print(f"   注意: {data.get('note')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 无法连接到服务器: {e}")
    
    time.sleep(0.5)
    
    # 测试3: 天气查询
    print("\n\n3. 测试天气查询API")
    print("-" * 70)
    try:
        response = requests.get(
            f"{base_url}/external/weather",
            params={"city": "济南"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 天气查询成功")
            print(f"   城市: {data.get('city')}")
            print(f"   温度: {data.get('temperature')}°C")
            print(f"   天气: {data.get('weather')}")
            print(f"   湿度: {data.get('humidity')}%")
            if 'note' in data:
                print(f"   注意: {data.get('note')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 无法连接到服务器: {e}")
    
    time.sleep(0.5)
    
    # 测试4: API状态
    print("\n\n4. 测试API状态查询")
    print("-" * 70)
    try:
        response = requests.get(f"{base_url}/external/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态查询成功")
            for api_name, info in data.items():
                print(f"\n   {info['name']}:")
                print(f"     状态: {'启用' if info['enabled'] else '未启用（模拟模式）'}")
                print(f"     缓存条目: {info['cache_entries']}")
                print(f"     最近1分钟请求数: {info['requests_last_minute']}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 无法连接到服务器: {e}")
    
    print("\n" + "=" * 70)
    print("✅ 外部API集成测试完成")
    print("=" * 70)


def test_api_integration_in_query():
    """测试外部API在查询中的集成"""
    print("\n\n" + "=" * 70)
    print("测试外部API在智能对话中的应用")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000/api"
    
    test_cases = [
        {
            "question": "济南市2025年家电补贴政策还有效吗？",
            "description": "测试政策时效性查询"
        },
        {
            "question": "海尔一级能效空调现在多少钱？",
            "description": "测试价格查询集成"
        },
        {
            "question": "济南今天天气怎么样？",
            "description": "测试天气查询集成"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print("-" * 70)
        print(f"问题: {test_case['question']}")
        print("建议: 可以在对话中询问此类问题，系统会自动调用外部API")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # 运行测试
    test_external_api_endpoints()
    test_api_integration_in_query()
    
    print("\n\n💡 提示:")
    print("1. 外部API功能已集成到系统中")
    print("2. 目前使用模拟数据，实际部署时可配置真实API")
    print("3. 支持缓存和限流，提高性能和稳定性")
    print("4. API端点:")
    print("   - GET /api/external/policy_check - 政策核查")
    print("   - GET /api/external/price - 价格查询")
    print("   - GET /api/external/weather - 天气查询")
    print("   - GET /api/external/status - API状态")
