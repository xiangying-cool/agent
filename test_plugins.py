"""测试插件系统"""
from plugin_manager import PluginManager

# 初始化插件管理器
manager = PluginManager()
manager.load_all_plugins()

print("\n" + "="*60)
print("测试价格比较插件")
print("="*60)

# 测试价格比较
context = {
    "products": ["冰箱", "洗衣机", "电视"],
    "budget": 10000
}

result = manager.execute_plugin("price_comparator", context)
print(f"\n状态: {result['status']}")
print(f"总节省: ¥{result['total_savings']}")
print("\n价格对比:")
for item in result['comparisons']:
    print(f"  {item['product']}:")
    print(f"    京东: ¥{item['jd_price']}")
    print(f"    淘宝: ¥{item['taobao_price']}")
    print(f"    最优平台: {item['best_platform']} (节省¥{item['savings']})")
    print(f"    购买链接: {item['url']}")

print("\n" + "="*60)
print("测试报告生成插件")
print("="*60)

# 测试报告生成
report_context = {
    "recommendation": {
        "total_subsidy": 2325,
        "products": ["冰箱", "洗衣机"]
    },
    "format": "pdf"
}

report_result = manager.execute_plugin("report_generator", report_context)
print(f"\n状态: {report_result['status']}")
print(f"文件名: {report_result['filename']}")
print(f"格式: {report_result['format']}")
print(f"大小: {report_result['size']}")

print("\n" + "="*60)
print("插件信息")
print("="*60)

for plugin_name in manager.get_available_plugins():
    info = manager.get_plugin_info(plugin_name)
    print(f"\n{info['name']} v{info['version']}")
    print(f"  描述: {info['description']}")
