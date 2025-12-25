"""
简化向量嵌入 - 使用TF-IDF代替HuggingFace模型（无需下载）
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List
import numpy as np
import pickle
import os


class SimpleEmbeddings:
    """简单的TF-IDF向量化器，无需下载模型"""
    
    def __init__(self, model_path: str = "./tfidf_model.pkl"):
        self.model_path = model_path
        self.vectorizer = None
        self.corpus = []
        
        # 尝试加载已有模型
        if os.path.exists(model_path):
            self.load_model()
    
    def fit(self, texts: List[str]):
        """训练向量化器"""
        self.corpus = texts
        self.vectorizer = TfidfVectorizer(
            max_features=384,  # 向量维度
            ngram_range=(1, 2),  # 使用1-gram和2-gram
            max_df=0.85,
            min_df=2
        )
        self.vectorizer.fit(texts)
        self.save_model()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """将文档转换为向量"""
        if self.vectorizer is None:
            raise ValueError("模型未训练，请先调用fit()方法")
        
        vectors = self.vectorizer.transform(texts).toarray()
        return vectors.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """将查询转换为向量"""
        if self.vectorizer is None:
            raise ValueError("模型未训练，请先调用fit()方法")
        
        vector = self.vectorizer.transform([text]).toarray()[0]
        return vector.tolist()
    
    def __call__(self, text: str) -> List[float]:
        """使对象可调用，兼容LangChain"""
        return self.embed_query(text)
    
    def save_model(self):
        """保存模型"""
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        print(f"✓ 向量模型已保存到 {self.model_path}")
    
    def load_model(self):
        """加载模型"""
        with open(self.model_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        print(f"✓ 向量模型已从 {self.model_path} 加载")


if __name__ == "__main__":
    # 测试
    embeddings = SimpleEmbeddings()
    
    test_texts = [
        "家电以旧换新补贴政策",
        "手机购新补贴标准",
        "汽车消费券发放"
    ]
    
    embeddings.fit(test_texts)
    
    # 测试嵌入
    query_vec = embeddings.embed_query("补贴金额是多少")
    print(f"查询向量维度: {len(query_vec)}")
    
    doc_vecs = embeddings.embed_documents(test_texts)
    print(f"文档向量数量: {len(doc_vecs)}")
    print(f"每个向量维度: {len(doc_vecs[0])}")
