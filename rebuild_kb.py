"""
重新构建知识库 - 加载新的政策文件
使用 sync_knowledge_base 增量更新
"""
import os
import sys
from knowledge_base import KnowledgeBase
import config

def update_knowledge_base():
    """增量更新知识库"""
    
    print("="*60)
    print("知识库增量更新工具")
    print("="*60)
    
    # 需要添加的新文档目录
    new_docs_dir = "./2025年家电和数码以旧换新政策文件/济南市以旧换新政策数据集"
    old_docs_dir = config.DOCS_DIR  # 原有知识库目录
    
    if not os.path.exists(new_docs_dir):
        print(f"错误: 找不到目录 {new_docs_dir}")
        return
    
    # 统计文件
    new_pdf_files = [f for f in os.listdir(new_docs_dir) if f.endswith('.pdf')]
    print(f"\n发现新文件: {len(new_pdf_files)} 个PDF")
    
    # 复制新文件到原有知识库目录
    print(f"\n步骤1: 复制新文件到 {old_docs_dir}")
    import shutil
    copied_count = 0
    for pdf_file in new_pdf_files:
        src = os.path.join(new_docs_dir, pdf_file)
        dst = os.path.join(old_docs_dir, pdf_file)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"  ✓ 复制: {pdf_file}")
            copied_count += 1
        else:
            print(f"  - 跳过: {pdf_file} (已存在)")
    
    print(f"\n✓ 复制了 {copied_count} 个新文件")
    
    # 使用 sync_knowledge_base 增量更新
    print("\n步骤2: 增量同步知识库...")
    kb = KnowledgeBase()
    kb.sync_knowledge_base(force_rebuild_on_modified=False)
    
    print("\n步骤3: 测试查询...")
    test_queries = [
        "济南市家电以旧换新补贴标准",
        "电动自行车以旧换新政策",
        "汽车报废更新补贴"
    ]
    
    for query in test_queries:
        results = kb.search(query, top_k=2)
        print(f"\n查询: '{query}'")
        print(f"返回 {len(results)} 个结果:")
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            print(f"  {i}. {source[:60]}...")
    
    # 统计信息
    stats = kb.get_stats()
    
    print("\n" + "="*60)
    print("✓ 知识库更新完成！")
    print("="*60)
    print("\n知识库统计:")
    print(f"  总文档数: {stats.get('total_documents', 0)}")
    print(f"  总文本块: {stats.get('total_chunks', 0)}")
    print(f"  新增文件: {copied_count} 个")
    print(f"  存储位置: {config.CHROMA_DB_DIR}")
    print("\n现在可以启动智能体服务了: python app.py")
    
    # 5. 测试查询
    print("\n步骤5: 测试查询...")
    test_queries = [
        "济南市家电以旧换新补贴标准",
        "电动自行车以旧换新政策",
        "汽车报废更新补贴"
    ]
    
    for query in test_queries:
        results = kb.search(query, top_k=2)
        print(f"\n查询: '{query}'")
        print(f"返回 {len(results)} 个结果:")
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            print(f"  {i}. {source[:60]}...")
    
    print("\n现在可以启动智能体服务了: python app.py")

if __name__ == "__main__":
    try:
        update_knowledge_base()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
