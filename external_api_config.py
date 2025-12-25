"""
外部API配置文件
用于管理API密钥和启用状态
"""
import os

# API配置
EXTERNAL_API_CONFIG = {
    # 价格比价API配置 (京东联盟)
    "price": {
        "enabled": True,  # 已启用
        "app_key": "6ef3fbb8dfe5d8e2957b76cbf1e4f9572f33dad4b35487b5032d598d18effa2b4f40d5377c5544e5",
        "app_secret": os.getenv("JD_APP_SECRET", ""),  # 京东 AppSecret，用于签名
        "base_url": "https://api.jd.com/routerjson",  # 京东联盟API地址
        "timeout": 5,
        # 京东联盟开放平台: https://union.jd.com/
        # API文档: https://union.jd.com/myTools/myApi
        # 注意: app_key 是您的AppKey, app_secret 需要单独配置
    },
    
    # 政策核查API配置 (政府开放数据平台)
    "policy_check": {
        "enabled": False,  # 改为True启用
        "api_key": os.getenv("GOV_API_KEY", ""),
        "base_url": "http://www.jinan.gov.cn/api/policy",  # 修改为真实API地址
        "timeout": 10,
        # 可选的政府数据平台:
        # - 国家政务服务平台: https://www.gjzwfw.gov.cn/
        # - 山东政务服务网: https://www.sd.gov.cn/
        # - 济南政府网: http://www.jinan.gov.cn/
    },
}

# API认证头配置
def get_api_headers(api_name: str) -> dict:
    """获取API请求头"""
    config = EXTERNAL_API_CONFIG.get(api_name, {})
    api_key = config.get("api_key", "")
    
    headers = {
        "User-Agent": "IntelliPolicy/1.0",
        "Content-Type": "application/json"
    }
    
    # 根据不同API添加认证头
    if api_name == "price" and api_key:
        # 京东联盟使用签名方式，具体看文档
        headers["Authorization"] = f"Bearer {api_key}"
    elif api_name == "policy_check" and api_key:
        headers["X-API-Key"] = api_key
    
    return headers


# 快速启用配置示例
def enable_price_api(api_key: str, base_url: str = None):
    """快速启用价格API"""
    EXTERNAL_API_CONFIG["price"]["enabled"] = True
    EXTERNAL_API_CONFIG["price"]["api_key"] = api_key
    if base_url:
        EXTERNAL_API_CONFIG["price"]["base_url"] = base_url
    print(f"✅ 价格API已启用")


def enable_policy_api(api_key: str = "", base_url: str = None):
    """快速启用政策API"""
    EXTERNAL_API_CONFIG["policy_check"]["enabled"] = True
    if api_key:
        EXTERNAL_API_CONFIG["policy_check"]["api_key"] = api_key
    if base_url:
        EXTERNAL_API_CONFIG["policy_check"]["base_url"] = base_url
    print(f"✅ 政策核查API已启用")


# 配置验证
def validate_config():
    """验证API配置"""
    issues = []
    
    for api_name, config in EXTERNAL_API_CONFIG.items():
        if config.get("enabled"):
            if not config.get("api_key") and api_name != "policy_check":
                issues.append(f"⚠️ {api_name}: API已启用但未配置密钥")
            if not config.get("base_url"):
                issues.append(f"❌ {api_name}: 缺少base_url配置")
    
    if issues:
        print("\n配置问题:")
        for issue in issues:
            print(f"  {issue}")
        return False
    
    enabled_count = sum(1 for c in EXTERNAL_API_CONFIG.values() if c.get("enabled"))
    print(f"✅ 配置验证通过，已启用 {enabled_count} 个API")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("外部API配置检查")
    print("=" * 60)
    
    # 显示当前配置
    print("\n当前配置状态:")
    for api_name, config in EXTERNAL_API_CONFIG.items():
        status = "✅ 已启用" if config["enabled"] else "⚪ 未启用"
        has_key = "🔑 有密钥" if config.get("api_key") else "🔓 无密钥"
        print(f"  {api_name}: {status} | {has_key}")
    
    print("\n" + "-" * 60)
    validate_config()
    
    print("\n" + "=" * 60)
    print("启用示例:")
    print("=" * 60)
    print("""
# 京东联盟API已配置，可以直接使用

# 如需启用其他API:
# 修改 external_api_config.py 文件
# 将 "enabled": False 改为 True
# 将 "api_key": "" 改为你的密钥
    """)
