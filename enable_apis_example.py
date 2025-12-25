"""
快速启用外部API示例
演示如何配置和启用真实的外部API
"""
from external_api_config import (
    enable_weather_api,
    enable_price_api, 
    enable_policy_api,
    validate_config,
    EXTERNAL_API_CONFIG
)

def example_enable_weather():
    """示例：启用天气API"""
    print("\n" + "=" * 60)
    print("示例1: 启用OpenWeatherMap天气API")
    print("=" * 60)
    
    print("\n步骤:")
    print("1. 访问 https://openweathermap.org/api")
    print("2. 注册免费账号")
    print("3. 在API Keys页面获取密钥")
    print("4. 运行以下代码:")
    print()
    print("```python")
    print("from external_api_config import enable_weather_api")
    print('enable_weather_api("你的API密钥")')
    print("```")
    print()
    print("或者使用环境变量:")
    print("PowerShell: $env:OPENWEATHER_API_KEY='你的密钥'")
    print("Bash: export OPENWEATHER_API_KEY='你的密钥'")
    
    # 取消注释以下行并填入真实API密钥来启用
    # enable_weather_api("your_api_key_here")


def example_enable_price():
    """示例：启用价格API"""
    print("\n" + "=" * 60)
    print("示例2: 启用价格比价API")
    print("=" * 60)
    
    print("\n可选的价格API服务商:")
    print("1. 京东联盟开放平台: https://union.jd.com/")
    print("   - 提供商品价格、佣金等信息")
    print("   - 需要注册并申请API权限")
    print()
    print("2. 淘宝联盟: https://pub.alimama.com/")
    print("   - 提供淘宝/天猫商品信息")
    print("   - 需要加入淘宝联盟并获取密钥")
    print()
    print("3. 其他电商开放平台")
    print("   - 拼多多开放平台")
    print("   - 苏宁开放平台等")
    print()
    print("启用代码:")
    print("```python")
    print("from external_api_config import enable_price_api")
    print('enable_price_api(')
    print('    api_key="你的API密钥",')
    print('    base_url="https://api.实际服务商.com/price"')
    print(')')
    print("```")
    
    # 取消注释以下行并填入真实配置来启用
    # enable_price_api(
    #     api_key="your_api_key",
    #     base_url="https://api.example.com/price"
    # )


def example_enable_policy():
    """示例：启用政策核查API"""
    print("\n" + "=" * 60)
    print("示例3: 启用政策核查API")
    print("=" * 60)
    
    print("\n可用的政府数据平台:")
    print("1. 国家政务服务平台: https://www.gjzwfw.gov.cn/")
    print("   - 提供全国政务数据")
    print("   - 需要申请开放数据权限")
    print()
    print("2. 山东政务服务网: https://www.sd.gov.cn/")
    print("   - 山东省政务数据")
    print("   - 部分数据公开可查询")
    print()
    print("3. 济南市政府: http://www.jinan.gov.cn/")
    print("   - 济南市本地政策")
    print("   - 可能需要对接政府部门")
    print()
    print("启用代码:")
    print("```python")
    print("from external_api_config import enable_policy_api")
    print('enable_policy_api(')
    print('    api_key="",  # 如果需要')
    print('    base_url="http://api.gov.cn/policy"')
    print(')')
    print("```")
    
    # 取消注释以下行并填入真实配置来启用
    # enable_policy_api(
    #     base_url="http://www.jinan.gov.cn/api/policy"
    # )


def show_current_status():
    """显示当前配置状态"""
    print("\n" + "=" * 60)
    print("当前API配置状态")
    print("=" * 60)
    
    for api_name, config in EXTERNAL_API_CONFIG.items():
        print(f"\n{config.get('name', api_name)}:")
        print(f"  URL: {config['base_url']}")
        print(f"  状态: {'✅ 已启用' if config['enabled'] else '⚪ 未启用'}")
        print(f"  密钥: {'🔑 已配置' if config.get('api_key') else '🔓 未配置'}")
        print(f"  超时: {config['timeout']}秒")


def quick_test():
    """快速测试已启用的API"""
    print("\n" + "=" * 60)
    print("测试已启用的API")
    print("=" * 60)
    
    from external_api_manager import external_api_manager
    
    enabled_apis = [
        name for name, config in EXTERNAL_API_CONFIG.items()
        if config['enabled']
    ]
    
    if not enabled_apis:
        print("\n⚠️ 当前没有启用任何API")
        print("请先配置并启用至少一个API")
        return
    
    print(f"\n已启用 {len(enabled_apis)} 个API: {', '.join(enabled_apis)}")
    
    # 测试天气API
    if "weather" in enabled_apis:
        print("\n测试天气API...")
        result = external_api_manager.get_weather("济南")
        if result.get("note"):
            print(f"⚠️ {result['note']}")
        else:
            print(f"✅ 天气: {result.get('weather')}, 温度: {result.get('temperature')}°C")
    
    # 测试价格API
    if "price" in enabled_apis:
        print("\n测试价格API...")
        result = external_api_manager.get_product_price("空调")
        if result.get("note"):
            print(f"⚠️ {result['note']}")
        else:
            print(f"✅ 最低价: ¥{result.get('lowest_price', 0):.2f}")
    
    # 测试政策API
    if "policy_check" in enabled_apis:
        print("\n测试政策核查API...")
        result = external_api_manager.check_policy_realtime("家电补贴政策")
        if result.get("note"):
            print(f"⚠️ {result['note']}")
        else:
            print(f"✅ 状态: {result.get('status')}")


if __name__ == "__main__":
    print("=" * 60)
    print("外部API启用指南")
    print("=" * 60)
    
    # 显示当前状态
    show_current_status()
    
    # 显示启用示例
    example_enable_weather()
    example_enable_price()
    example_enable_policy()
    
    # 验证配置
    print("\n" + "=" * 60)
    print("配置验证")
    print("=" * 60)
    validate_config()
    
    # 快速测试
    quick_test()
    
    # 使用提示
    print("\n" + "=" * 60)
    print("💡 使用提示")
    print("=" * 60)
    print("""
1. 推荐使用环境变量管理API密钥（更安全）
2. 生产环境不要将密钥硬编码在代码中
3. 可以在 external_api_config.py 中修改配置
4. 启用后重启服务器即可生效
5. 查看 EXTERNAL_API_README.md 了解更多信息

快速启用命令:
-----------
# Windows PowerShell
$env:OPENWEATHER_API_KEY="你的密钥"; python app.py

# Linux/Mac
export OPENWEATHER_API_KEY="你的密钥" && python app.py
    """)
