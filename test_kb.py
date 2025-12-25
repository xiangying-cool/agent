"""
测试更新后的知识库
"""
from knowledge_base import KnowledgeBase

def test_kb():
    kb = KnowledgeBase()
    kb.build_knowledge_base()
    
    print("="*60)
    print("知识库测试")
    print("="*60)
    
    test_queries = [
        "济南市家电以旧换新补贴标准",
        "电动自行车以旧换新政策",
        "汽车报废更新补贴",
        "3C产品购新补贴"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        results = kb.search(query, top_k=3)
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            preview = doc.page_content[:100].replace('\n', ' ')
            print(f"  {i}. {source}")
            print(f"     内容: {preview}...")
    
    # 显示统计信息
    stats = kb.get_stats()
    print("\n" + "="*60)
    print("知识库统计信息:")
    print(f"  总文档数: {stats.get('total_documents', 0)}")
    print(f"  总文本块: {stats.get('total_chunks', 0)}")
    print("="*60)

if __name__ == "__main__":
    test_kb()
