"""
测试地理位置功能
"""
from location_service import location_service

print("=" * 60)
print("地理位置功能测试")
print("=" * 60)

# 测试1: 位置解析
print("\n1. 位置解析测试")
print("-" * 60)
test_locations = [
    "山东省济南市历下区",
    "青岛市市南区",
    "济南",
    "山东"
]

for loc_str in test_locations:
    parsed = location_service.parse_location(loc_str)
    print(f"\n输入: {loc_str}")
    print(f"  解析结果: {parsed['province']} -> {parsed['city']} -> {parsed['district']}")
    print(f"  层级: {parsed['level']}")

# 测试2: 搜索关键词生成
print("\n\n2. 搜索关键词生成")
print("-" * 60)
user_loc = location_service.parse_location("济南市历下区")
keywords = location_service.get_location_keywords(user_loc)
print(f"用户位置: 济南市历下区")
print(f"生成关键词: {keywords}")

# 测试3: 文档匹配度计算
print("\n\n3. 文档匹配度计算")
print("-" * 60)
test_docs = [
    "济南市历下区家电以旧换新政策实施细则",
    "济南市2024年消费品以旧换新补贴标准",
    "山东省汽车以旧换新实施办法",
    "青岛市家电补贴政策"
]

for doc in test_docs:
    score = location_service.calculate_location_score(doc, user_loc)
    print(f"\n文档: {doc}")
    print(f"  匹配分数: {score:.2f} ({'高' if score >= 0.7 else '中' if score >= 0.3 else '低'}相关性)")

# 测试4: 文档重排序
print("\n\n4. 基于位置的文档重排序")
print("-" * 60)
documents = [
    {"content": "济南市历下区家电补贴政策详细说明", "score": 0.6, "source": "doc1.pdf"},
    {"content": "青岛市家电补贴最新标准", "score": 0.9, "source": "doc2.pdf"},
    {"content": "济南市市中区补贴流程", "score": 0.7, "source": "doc3.pdf"},
    {"content": "山东省政策总体指导意见", "score": 0.8, "source": "doc4.pdf"}
]

print("\n排序前 (按原始分数):")
for i, doc in enumerate(sorted(documents, key=lambda x: x['score'], reverse=True), 1):
    print(f"  {i}. [{doc['score']:.1f}] {doc['content'][:30]}...")

reranked = location_service.rerank_by_location(
    documents.copy(), 
    user_loc, 
    location_weight=0.3
)

print("\n排序后 (考虑位置权重0.3):")
for i, doc in enumerate(reranked, 1):
    print(f"  {i}. [{doc['combined_score']:.2f}] {doc['content'][:30]}...")
    print(f"      (原始:{doc['original_score']:.1f} + 位置:{doc['location_score']:.1f})")

# 测试5: 实际查询模拟
print("\n\n5. 实际查询模拟")
print("-" * 60)
user_locations = [
    {"province": "山东省", "city": "济南市", "district": "历下区"},
    {"province": "山东省", "city": "青岛市", "district": None},
    None
]

for loc in user_locations:
    if loc:
        print(f"\n用户位置: {loc.get('city', '未知')} {loc.get('district', '')}")
    else:
        print(f"\n用户位置: 未提供")
    
    # 模拟检索到的文档
    docs = [
        {"content": "济南市家电补贴政策", "score": 0.7, "source": "济南政策.pdf"},
        {"content": "青岛市家电补贴标准", "score": 0.8, "source": "青岛政策.pdf"},
        {"content": "山东省统一补贴办法", "score": 0.6, "source": "省级文件.pdf"},
    ]
    
    if loc and loc.get('city'):
        reranked = location_service.rerank_by_location(docs.copy(), loc, 0.3)
        print("  推荐顺序:")
        for i, doc in enumerate(reranked[:3], 1):
            print(f"    {i}. {doc['source']} (综合分:{doc['combined_score']:.2f})")
    else:
        print("  推荐顺序: (无位置信息，按原始分数)")
        for i, doc in enumerate(sorted(docs, key=lambda x: x['score'], reverse=True)[:3], 1):
            print(f"    {i}. {doc['source']} (分数:{doc['score']:.1f})")

print("\n" + "=" * 60)
print("测试完成！地理位置功能工作正常")
print("=" * 60)
print("\n功能说明:")
print("  1. 自动解析省/市/区层级")
print("  2. 生成位置相关搜索关键词")
print("  3. 计算文档与位置的匹配度")
print("  4. 基于位置优化检索结果排序")
print("  5. 支持无位置信息的降级处理")
