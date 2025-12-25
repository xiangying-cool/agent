"""
Reranker模块 - 检索结果重排序
解决向量检索噪音高的问题，通过二次排序保证模型看到真正关键的政策片段
"""
from typing import List, Tuple
from langchain.schema import Document
import config
try:
    from sentence_transformers import CrossEncoder
    CROSSENCODER_AVAILABLE = True
except ImportError:
    CROSSENCODER_AVAILABLE = False
    print("警告: sentence-transformers 未安装，将使用关键词重排")

try:
    from rank_bm25 import BM25Okapi
    import jieba
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    print("警告: rank-bm25 或 jieba 未安装，BM25 检索不可用")


class Reranker:
    """重排序器"""
    
    def __init__(self):
        self.method = config.RERANKER_MODEL
        self.cross_encoder = None
        
        # 如果配置使用 CrossEncoder 且可用，则加载模型
        if self.method == "cross-encoder" and CROSSENCODER_AVAILABLE:
            try:
                print("正在加载 CrossEncoder 模型...")
                self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
                print("✓ CrossEncoder 加载成功")
            except Exception as e:
                print(f"CrossEncoder 加载失败: {e}，回退到关键词重排")
                self.cross_encoder = None
    
    def rerank(self, 
               query: str, 
               documents: List[Document],
               top_k: int = None) -> List[Tuple[Document, float]]:
        """
        对检索结果进行重排序
        
        Args:
            query: 用户查询
            documents: 检索到的文档列表
            top_k: 返回前k个结果
            
        Returns:
            [(Document, score), ...] 按相关性降序排列
        """
        if top_k is None:
            top_k = config.RERANK_TOP_K
        
        if self.method == "cross-encoder":
            return self._cross_encoder_rerank(query, documents, top_k)
        else:
            # 默认使用关键词匹配重排
            return self._keyword_rerank(query, documents, top_k)
    
    def _cross_encoder_rerank(self,
                             query: str,
                             documents: List[Document],
                             top_k: int) -> List[Tuple[Document, float]]:
        """
        使用交叉编码器重排
        """
        if self.cross_encoder is not None:
            # 使用真实 CrossEncoder 模型
            pairs = [[query, doc.page_content[:512]] for doc in documents]  # 截断到512字符
            scores = self.cross_encoder.predict(pairs)
            
            # 组合文档和分数
            scored_docs = list(zip(documents, scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            return scored_docs[:top_k]
        else:
            # 回退到关键词匹配（原有逻辑）
            scored_docs = []
            query_terms = set(query)
            
            for doc in documents:
                doc_text = doc.page_content
                
                # 1. 精确匹配得分
                exact_match_score = sum(
                    1 for term in query_terms if term in doc_text
                ) / max(len(query_terms), 1)
                
                # 2. 长度惩罚
                ideal_length = 500
                length_penalty = 1.0 - abs(len(doc_text) - ideal_length) / ideal_length
                length_penalty = max(0.5, min(1.0, length_penalty))
                
                # 3. 位置加权
                position_bonus = 0
                if any(term in doc_text[:100] for term in query_terms):
                    position_bonus = 0.2
                
                score = exact_match_score * 0.6 + length_penalty * 0.2 + position_bonus * 0.2
                scored_docs.append((doc, score))
            
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return scored_docs[:top_k]
    
    def _keyword_rerank(self,
                       query: str,
                       documents: List[Document],
                       top_k: int) -> List[Tuple[Document, float]]:
        """基于关键词匹配的简单重排"""
        # 政策相关的高价值关键词
        high_value_keywords = [
            "补贴", "标准", "金额", "比例", "上限", "条件",
            "流程", "申请", "时间", "范围", "要求", "规定"
        ]
        
        scored_docs = []
        
        for doc in documents:
            doc_text = doc.page_content
            
            # 计算高价值关键词出现次数
            keyword_count = sum(
                doc_text.count(kw) for kw in high_value_keywords
            )
            
            # 计算查询词出现次数
            query_match_count = sum(
                doc_text.count(term) for term in query if len(term) > 1
            )
            
            # 综合得分
            score = keyword_count * 0.4 + query_match_count * 0.6
            
            scored_docs.append((doc, score))
        
        # 排序
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        return scored_docs[:top_k]
    
    def explain_ranking(self, 
                       query: str,
                       ranked_docs: List[Tuple[Document, float]]) -> str:
        """解释重排序结果"""
        explanation = f"重排序结果（共{len(ranked_docs)}条）：\n\n"
        
        for i, (doc, score) in enumerate(ranked_docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            preview = doc.page_content[:100] + "..."
            
            explanation += f"{i}. [{source}] (得分: {score:.3f})\n"
            explanation += f"   内容预览: {preview}\n\n"
        
        return explanation


class HybridRetriever:
    """混合检索器 - 结合向量检索和 BM25 关键词检索"""
    
    def __init__(self, vector_store, reranker: Reranker = None):
        self.vector_store = vector_store
        self.reranker = reranker or Reranker()
        self.bm25_index = None
        self.bm25_documents = []
        
        # 如果 BM25 可用，构建索引
        if BM25_AVAILABLE:
            self._build_bm25_index()
    
    def _build_bm25_index(self):
        """构建 BM25 索引"""
        try:
            # 从 vectorstore 提取所有文档
            all_docs = self.vector_store.similarity_search("", k=1000)  # 获取尽可能多的文档
            if not all_docs:
                return
            
            self.bm25_documents = all_docs
            # 中文分词
            tokenized_corpus = [list(jieba.cut(doc.page_content)) for doc in all_docs]
            self.bm25_index = BM25Okapi(tokenized_corpus)
            print(f"✓ BM25 索引构建完成，共 {len(all_docs)} 个文档")
        except Exception as e:
            print(f"BM25 索引构建失败: {e}")
            self.bm25_index = None
    
    def retrieve(self, 
                query: str,
                top_k: int = None,
                use_rerank: bool = True) -> List[Document]:
        """
        混合检索
        
        Args:
            query: 用户查询
            top_k: 返回文档数量
            use_rerank: 是否使用重排序
            
        Returns:
            检索到的文档列表
        """
        if top_k is None:
            top_k = config.TOP_K
        
        # 1. 向量检索
        vector_results = self.vector_store.similarity_search(
            query, 
            k=top_k * 2  # 检索更多候选，后续重排
        )
        
        # 2. 关键词检索（简化实现）
        # 实际可使用 BM25 等算法
        keyword_results = self._keyword_search(query, top_k)
        
        # 3. 合并去重
        all_results = self._merge_results(vector_results, keyword_results)
        
        # 4. 重排序
        if use_rerank and config.USE_RERANKER:
            ranked_results = self.reranker.rerank(query, all_results, top_k)
            return [doc for doc, score in ranked_results]
        else:
            return all_results[:top_k]
    
    def _keyword_search(self, query: str, top_k: int) -> List[Document]:
        """关键词检索（使用 BM25）"""
        if self.bm25_index is None or not BM25_AVAILABLE:
            return []
        
        try:
            # 中文分词
            tokenized_query = list(jieba.cut(query))
            # BM25 计分
            scores = self.bm25_index.get_scores(tokenized_query)
            # 获取 top_k 索引
            import numpy as np
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            # 返回文档
            return [self.bm25_documents[i] for i in top_indices if i < len(self.bm25_documents)]
        except Exception as e:
            print(f"BM25 检索失败: {e}")
            return []
    
    def _merge_results(self, 
                      vector_results: List[Document],
                      keyword_results: List[Document]) -> List[Document]:
        """合并并去重检索结果"""
        seen = set()
        merged = []
        
        # 优先保留向量检索结果
        for doc in vector_results:
            doc_id = doc.page_content[:100]  # 简单去重
            if doc_id not in seen:
                seen.add(doc_id)
                merged.append(doc)
        
        # 添加关键词检索结果
        for doc in keyword_results:
            doc_id = doc.page_content[:100]
            if doc_id not in seen:
                seen.add(doc_id)
                merged.append(doc)
        
        return merged


if __name__ == "__main__":
    # 测试重排序器
    from langchain.schema import Document
    
    # 模拟检索结果
    test_docs = [
        Document(
            page_content="济南市家电以旧换新补贴标准：按购新金额的10%给予补贴，单台最高不超过1000元。",
            metadata={"source": "济南市家电补贴政策.pdf"}
        ),
        Document(
            page_content="本次活动时间为2025年1月1日至12月31日，请在规定时间内申请。",
            metadata={"source": "活动公告.pdf"}
        ),
        Document(
            page_content="补贴范围包括电视机、冰箱、洗衣机、空调等大家电产品。",
            metadata={"source": "补贴范围说明.pdf"}
        ),
    ]
    
    print("="*60)
    print("Reranker测试")
    print("="*60)
    
    reranker = Reranker()
    
    query = "家电补贴标准是多少"
    
    print(f"\n查询: {query}")
    print(f"\n原始检索结果（{len(test_docs)}条）:")
    for i, doc in enumerate(test_docs, 1):
        print(f"{i}. {doc.metadata['source']}")
        print(f"   {doc.page_content[:50]}...")
    
    # 重排序
    ranked = reranker.rerank(query, test_docs, top_k=2)
    
    print(f"\n重排序后（Top {len(ranked)}）:")
    for i, (doc, score) in enumerate(ranked, 1):
        print(f"{i}. {doc.metadata['source']} (得分: {score:.3f})")
        print(f"   {doc.page_content[:50]}...")
    
    print("\n" + "="*60)
