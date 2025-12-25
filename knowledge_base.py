"""
知识库模块 - 构建和检索向量数据库
"""
import os
import sys

# 禁用ChromaDB遥测（必须在导入chromadb之前设置）
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_TELEMETRY'] = 'False'

# 解决SQLite版本问题 - 方案1: 尝试使用pysqlite3
try:
    __import__('pysqlite3')
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # 方案2: 禁用ChromaDB的SQLite版本检查
    import sqlite3
    # 强制设置sqlite版本（绕过检查）
    sqlite3.sqlite_version_info = (3, 35, 0)
    sqlite3.sqlite_version = '3.35.0'

from typing import List
from langchain_community.vectorstores import FAISS  # 使用FAISS代替Chroma
from langchain.schema import Document
from document_loader import DocumentLoader
from simple_embeddings import SimpleEmbeddings  # 使用简化向量模型
import config
import json
import hashlib


class KnowledgeBase:
    """知识库管理"""
    
    def __init__(self):
        print("正在加载向量模型...")
        
        # 使用简化的TF-IDF向量化器（无需下载模型）
        self.embeddings = SimpleEmbeddings()
        self.vectorstore = None
        self.doc_loader = DocumentLoader()
        print("✓ 向量模型加载成功（使用TF-IDF）")
        self._registry_file = os.path.join(config.METADATA_KB_DIR, "policy_registry.json")
        self._boosts_file = os.path.join(config.METADATA_KB_DIR, "boosts.json")
    
    def build_knowledge_base(self, force_rebuild: bool = False):
        """构建知识库"""
        faiss_index_path = os.path.join(config.CHROMA_DB_DIR, "faiss_index")
        
        if os.path.exists(faiss_index_path) and not force_rebuild:
            print("加载已有知识库...")
            self.vectorstore = FAISS.load_local(
                faiss_index_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"知识库加载完成")
        else:
            print("开始构建知识库...")
            
            # 加载所有文档
            documents = self.doc_loader.load_all_documents(config.DOCS_DIR)
            print(f"加载了 {len(documents)} 个文档")
            
            # 切分文档
            chunks = self.doc_loader.split_documents(documents)
            print(f"切分成 {len(chunks)} 个文本块")
            
            # 训练TF-IDF模型
            if chunks:
                print("正在训练向量模型...")
                texts = [chunk.page_content for chunk in chunks]
                self.embeddings.fit(texts)
                
                # 创建向量数据库（使用FAISS）
                print("正在构建 FAISS 索引...")
                self.vectorstore = FAISS.from_documents(
                    documents=chunks,
                    embedding=self.embeddings
                )
                
                # 保存索引
                os.makedirs(config.CHROMA_DB_DIR, exist_ok=True)
                self.vectorstore.save_local(faiss_index_path)
                print(f"知识库构建完成！存储路径: {faiss_index_path}")
            else:
                print("警告: 没有找到有效的文档内容")
    
    def search(self, query: str, top_k: int = None) -> List[Document]:
        """检索相关文档(优化版:增加阈值过滤)"""
        if self.vectorstore is None:
            raise ValueError("知识库未初始化，请先调用 build_knowledge_base()")
        
        if top_k is None:
            top_k = config.TOP_K
        
        # 检索更多结果用于阈值过滤
        results_with_scores = self.vectorstore.similarity_search_with_score(query, k=top_k * 2)
        
        # 按相似度阈值过滤
        filtered_results = [
            doc for doc, score in results_with_scores 
            if score < (1.0 - config.SIMILARITY_THRESHOLD)  # FAISS使用距离，越小越相似
        ][:top_k]
        
        return filtered_results if filtered_results else [doc for doc, _ in results_with_scores[:top_k]]
    
    def sync_knowledge_base(self, force_rebuild_on_modified: bool = True):
        """增量同步：新增文件增量写入；有修改则重建索引"""
        os.makedirs(config.METADATA_KB_DIR, exist_ok=True)
        registry = self._load_registry()
        # 扫描当前文档
        documents = self.doc_loader.load_all_documents(config.DOCS_DIR)
        new_docs = []
        modified_detected = False
        for doc in documents:
            fp = doc.metadata.get("file_path")
            try:
                mtime = os.path.getmtime(fp)
            except Exception:
                mtime = 0
            content_sample = doc.page_content[:10000]
            h = hashlib.md5(content_sample.encode("utf-8", errors="ignore")).hexdigest()
            key = doc.metadata.get("source", os.path.basename(fp))
            prev = registry.get(key)
            if not prev:
                new_docs.append(doc)
                registry[key] = {"file_path": fp, "mtime": mtime, "hash": h}
            else:
                if prev.get("hash") != h or prev.get("mtime") != mtime:
                    modified_detected = True
                    registry[key] = {"file_path": fp, "mtime": mtime, "hash": h}
        if self.vectorstore is None:
            # 初次
            self.build_knowledge_base(force_rebuild=False)
        else:
            if modified_detected and force_rebuild_on_modified:
                # 存在修改，重建全量索引避免重复
                self.build_knowledge_base(force_rebuild=True)
            elif new_docs:
                # 对新增文档执行增量索引
                chunks = self.doc_loader.split_documents(new_docs)
                if chunks:
                    self.vectorstore.add_documents(chunks)
                    faiss_index_path = os.path.join(config.CHROMA_DB_DIR, "faiss_index")
                    os.makedirs(config.CHROMA_DB_DIR, exist_ok=True)
                    self.vectorstore.save_local(faiss_index_path)
        self._save_registry(registry)
        print("知识库同步完成：新增", len(new_docs), "条；修改检测：", modified_detected)

    def _load_registry(self) -> dict:
        try:
            if os.path.isfile(self._registry_file):
                with open(self._registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_registry(self, data: dict):
        try:
            with open(self._registry_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("保存注册表失败:", e)


    def search_with_score(self, query: str, top_k: int = None) -> List[tuple]:
        """检索相关文档并返回相似度分数（按文档去重）"""
        if self.vectorstore is None:
            raise ValueError("知识库未初始化，请先调用 build_knowledge_base()")
        if top_k is None:
            top_k = config.TOP_K
        
        # 检索更多结果以便去重后仍有足够数据
        results = self.vectorstore.similarity_search_with_score(query, k=top_k * 3)
        boosted_results = self._apply_boosts(results)
        boosted_results.sort(key=lambda x: float(x[1]))
        
        # 按文档来源去重，保留每个文档的最佳匹配块
        seen_sources = set()
        deduplicated = []
        for doc, score in boosted_results:
            source = doc.metadata.get("source", "Unknown")
            if source not in seen_sources:
                seen_sources.add(source)
                deduplicated.append((doc, score))
                if len(deduplicated) >= top_k:
                    break
        
        return deduplicated

    def _infer_category(self, doc: Document) -> str:
        """根据文件名/内容粗略推断政策类别"""
        name = (doc.metadata.get("source") or "").lower()
        text = (doc.page_content or "").lower()
        keywords_oldnew = ["以旧换新", "实施细则", "实施方案", "补贴", "换新"]
        keywords_activity = ["消费券", "泉城购", "活动", "公告", "首保", "购新"]
        for kw in keywords_activity:
            if kw in name or kw in text:
                return "消费活动"
        for kw in keywords_oldnew:
            if kw in name or kw in text:
                return "以旧换新"
        return "其他"

    def _load_boosts(self) -> dict:
        try:
            if os.path.isfile(self._boosts_file):
                with open(self._boosts_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"source": {}, "category": {}}

    def _save_boosts(self, data: dict):
        try:
            os.makedirs(config.METADATA_KB_DIR, exist_ok=True)
            with open(self._boosts_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("保存boosts失败:", e)

    def get_boosts(self) -> dict:
        return self._load_boosts()

    def set_boost(self, target_type: str, key: str, weight: float) -> dict:
        """设置boost权重：target_type in {source, category}，weight为降低距离的数值(0~1建议)"""
        boosts = self._load_boosts()
        if target_type not in ("source", "category"):
            raise ValueError("target_type 必须为 source 或 category")
        boosts.setdefault(target_type, {})[key] = float(weight)
        self._save_boosts(boosts)
        return boosts

    def clear_boost(self, target_type: str, key: str) -> dict:
        boosts = self._load_boosts()
        if target_type in boosts and key in boosts[target_type]:
            del boosts[target_type][key]
        self._save_boosts(boosts)
        return boosts

    def _apply_boosts(self, results: List[tuple]) -> List[tuple]:
        """对检索结果应用boost：FAISS返回的是距离分数，越小越相似，因此降低分数实现提升"""
        boosts = self._load_boosts()
        adjusted = []
        for doc, score in results:
            bonus = 0.0
            source = doc.metadata.get("source", "Unknown")
            category = self._infer_category(doc)
            bonus += float(boosts.get("source", {}).get(source, 0.0))
            bonus += float(boosts.get("category", {}).get(category, 0.0))
            new_score = max(float(score) - bonus, 0.0)
            adjusted.append((doc, new_score))
        return adjusted

    def get_stats(self) -> dict:
        """获取知识库统计信息"""
        stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "documents_list": [],
            "index_path": os.path.join(config.CHROMA_DB_DIR, "faiss_index"),
            "registry_file": self._registry_file,
            "boosts_file": self._boosts_file,
            "boosts": self._load_boosts(),
        }
        registry = self._load_registry()
        stats["total_documents"] = len(registry)
        stats["documents_list"] = [
            {
                "source": key,
                "file_path": value.get("file_path", "Unknown"),
                "last_modified": value.get("mtime", 0),
            }
            for key, value in registry.items()
        ]
        if self.vectorstore is not None:
            try:
                stats["total_chunks"] = self.vectorstore.index.ntotal
            except Exception:
                stats["total_chunks"] = 0
        return stats

    def index_file(self, file_path: str) -> dict:
        """单文件快速入库（T+0）：解析、切分并增量写入索引，同时更新注册表"""
        text = self.doc_loader.load_document(file_path)
        if not text.strip():
            raise ValueError("文件内容为空或不可读取")
        doc = Document(page_content=text, metadata={"source": os.path.basename(file_path), "file_path": file_path})
        chunks = self.doc_loader.split_documents([doc])
        if self.vectorstore is None:
            # 若尚未初始化索引，则先构建
            self.build_knowledge_base(force_rebuild=False)
        if chunks:
            self.vectorstore.add_documents(chunks)
            faiss_index_path = os.path.join(config.CHROMA_DB_DIR, "faiss_index")
            os.makedirs(config.CHROMA_DB_DIR, exist_ok=True)
            self.vectorstore.save_local(faiss_index_path)
        # 更新注册表
        try:
            mtime = os.path.getmtime(file_path)
        except Exception:
            mtime = 0
        h = hashlib.md5(text[:10000].encode("utf-8", errors="ignore")).hexdigest()
        key = os.path.basename(file_path)
        registry = self._load_registry()
        registry[key] = {"file_path": file_path, "mtime": mtime, "hash": h}
        self._save_registry(registry)
        return {"message": "单文件入库完成", "added_chunks": len(chunks), "source": key}


if __name__ == "__main__":
    # 测试知识库构建
    kb = KnowledgeBase()
    kb.build_knowledge_base(force_rebuild=True)  # 强制重建
    
    # 测试检索
    test_queries = [
        "家电以旧换新补贴标准是多少？",
        "手机购新补贴如何申请？",
        "汽车消费补贴的时间范围"
    ]
    
    print("\n=== 检索测试 ===")
    for query in test_queries:
        print(f"\n问题: {query}")
        results = kb.search_with_score(query, top_k=2)
        for i, (doc, score) in enumerate(results, 1):
            print(f"\n结果 {i} (相似度: {score:.4f}):")
            print(f"来源: {doc.metadata.get('source', 'Unknown')}")
            print(f"内容: {doc.page_content[:150]}...")
