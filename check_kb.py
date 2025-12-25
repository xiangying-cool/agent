from knowledge_base import KnowledgeBase

kb = KnowledgeBase()
stats = kb.get_stats()

print('=' * 60)
print('知识库统计信息')
print('=' * 60)
print(f'文档数量: {stats["total_documents"]}')
print(f'文本块数: {stats["total_chunks"]}')
print(f'索引路径: {stats["index_path"]}')
print(f'注册表文件: {stats["registry_file"]}')

print('\n' + '=' * 60)
print('已导入文档列表')
print('=' * 60)

docs = stats['documents_list']
for i, doc in enumerate(docs, 1):
    print(f'{i}. {doc["source"]}')
    print(f'   文件路径: {doc["file_path"]}')
    print()
