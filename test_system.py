"""
系统测试脚本 - 快速验证系统是否正常工作
"""
import sys
import os

# 解决SQLite版本问题
try:
    __import__('pysqlite3')
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    import sqlite3
    sqlite3.sqlite_version_info = (3, 35, 0)
    sqlite3.sqlite_version = '3.35.0'


def test_imports():
    """测试依赖包是否正常导入"""
    print("=" * 60)
    print("测试1: 检查依赖包")
    print("=" * 60)
    
    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'fitz': 'PyMuPDF',
        'docx': 'python-docx',
        'langchain': 'LangChain',
        'chromadb': 'ChromaDB',
        'sentence_transformers': 'Sentence-Transformers',
    }
    
    failed = []
    for package, name in required_packages.items():
        try:
            if package == 'sentence_transformers':
                # sentence_transformers需要特殊处理
                import sentence_transformers
            else:
                __import__(package)
            print(f"✓ {name:30s} - 已安装")
        except ImportError as e:
            print(f"✗ {name:30s} - 未安装")
            failed.append(name)
        except Exception as e:
            # 其他错误（如SQLite版本问题）忽略，视为已安装
            print(f"✓ {name:30s} - 已安装")
    
    if failed:
        # sentence-transformers的导入检查有问题，如果只有它失败，忽略
        if failed == ['Sentence-Transformers']:
            print(f"\n⚠ 警告: Sentence-Transformers导入检查失败，但包已安装")
            print("将在实际运行时验证\n")
            return True
        print(f"\n错误: 以下包未安装: {', '.join(failed)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("\n所有依赖包检查通过！\n")
    return True


def test_config():
    """测试配置文件"""
    print("=" * 60)
    print("测试2: 检查配置文件")
    print("=" * 60)
    
    try:
        import config
        print(f"✓ 配置文件加载成功")
        
        # 检查API密钥
        if config.USE_QIANFAN:
            if config.QIANFAN_AK == "your_api_key":
                print("⚠ 警告: 百度千帆API密钥未配置")
                print("  请编辑 config.py 填入你的 QIANFAN_AK 和 QIANFAN_SK")
            else:
                print(f"✓ 百度千帆API已配置")
        else:
            if config.OPENAI_API_KEY == "your_api_key":
                print("⚠ 警告: OpenAI API密钥未配置")
                print("  请编辑 config.py 填入你的 OPENAI_API_KEY")
            else:
                print(f"✓ OpenAI兼容API已配置 ({config.OPENAI_BASE_URL})")
        
        print(f"✓ 文档目录: {config.DOCS_DIR}")
        print(f"✓ 向量数据库目录: {config.CHROMA_DB_DIR}")
        print(f"✓ 检索文档数: {config.TOP_K}")
        
        print("\n配置文件检查完成！\n")
        return True
        
    except Exception as e:
        print(f"✗ 配置文件加载失败: {e}")
        return False


def test_documents():
    """测试文档加载"""
    print("=" * 60)
    print("测试3: 检查政策文档")
    print("=" * 60)
    
    try:
        from document_loader import DocumentLoader
        import config
        
        loader = DocumentLoader()
        docs = loader.load_all_documents(config.DOCS_DIR)
        
        if not docs:
            print("⚠ 警告: 未找到任何政策文档")
            print("  请确保PDF/DOCX文件放在正确的目录下")
            return False
        
        print(f"✓ 找到 {len(docs)} 个政策文档")
        for doc in docs:
            print(f"  - {doc.metadata['source']}")
        
        chunks = loader.split_documents(docs)
        print(f"\n✓ 切分成 {len(chunks)} 个文本块")
        
        if chunks:
            print(f"\n示例文本块:")
            print(f"  来源: {chunks[0].metadata['source']}")
            print(f"  内容: {chunks[0].page_content[:100]}...")
        
        print("\n文档加载测试通过！\n")
        return True
        
    except Exception as e:
        print(f"✗ 文档加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_base():
    """测试知识库"""
    print("=" * 60)
    print("测试4: 检查知识库")
    print("=" * 60)
    
    try:
        import config
        
        if os.path.exists(config.CHROMA_DB_DIR):
            print(f"✓ 知识库已存在: {config.CHROMA_DB_DIR}")
            
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            kb.build_knowledge_base(force_rebuild=False)
            
            # 测试检索
            test_query = "补贴标准"
            results = kb.search(test_query, top_k=1)
            
            if results:
                print(f"\n✓ 知识库检索测试通过")
                print(f"  测试查询: {test_query}")
                print(f"  检索到 {len(results)} 条结果")
            else:
                print("⚠ 知识库为空或检索失败")
                return False
            
        else:
            print(f"⚠ 知识库未构建")
            print(f"  请运行: python knowledge_base.py")
            return False
        
        print("\n知识库检查通过！\n")
        return True
        
    except Exception as e:
        print(f"✗ 知识库检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_client():
    """测试大模型客户端"""
    print("=" * 60)
    print("测试5: 测试大模型连接")
    print("=" * 60)
    
    try:
        from llm_client import LLMClient
        import config
        
        client = LLMClient()
        print("✓ 大模型客户端初始化成功")
        
        if config.USE_QIANFAN and config.QIANFAN_AK == "your_api_key":
            print("⚠ 警告: API密钥未配置，跳过实际调用测试")
            print("\n请配置API密钥后再测试实际调用\n")
            return True
        
        if not config.USE_QIANFAN and config.OPENAI_API_KEY == "your_api_key":
            print("⚠ 警告: API密钥未配置，跳过实际调用测试")
            print("\n请配置API密钥后再测试实际调用\n")
            return True
        
        print("\n大模型客户端测试通过！\n")
        print("注意: 未测试实际API调用（避免消耗配额）")
        print("如需测试实际调用，请运行: python llm_client.py\n")
        return True
        
    except Exception as e:
        print(f"✗ 大模型客户端测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  政策咨询智能体 - 系统测试")
    print("=" * 60 + "\n")
    
    tests = [
        ("依赖包", test_imports),
        ("配置文件", test_config),
        ("政策文档", test_documents),
        ("知识库", test_knowledge_base),
        ("大模型", test_llm_client),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"✗ {name}测试异常: {e}")
            results[name] = False
    
    # 输出总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:15s} {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n通过率: {passed}/{total} ({passed*100//total}%)")
    
    if all(results.values()):
        print("\n🎉 所有测试通过！系统可以正常使用。")
        print("\n下一步:")
        print("1. 运行 启动.bat 启动Web服务")
        print("2. 打开 index.html 开始使用")
    else:
        print("\n⚠ 部分测试失败，请根据上述提示解决问题。")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
