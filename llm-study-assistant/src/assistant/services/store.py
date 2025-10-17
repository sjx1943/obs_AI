import os
import json
import numpy as np
from typing import List, Dict, Optional

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

class VectorStore:
    def __init__(self, data_dir: str, embedding_model_name: Optional[str] = None):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.meta_path = os.path.join(self.data_dir, "meta.jsonl")
        self.index_path = os.path.join(self.data_dir, "index.faiss")
        
        self.model = None
        self.index = None
        self.meta = []
        self.embedding_available = False

        if FAISS_AVAILABLE:
            try:
                model_name = embedding_model_name or os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
                self.model = SentenceTransformer(model_name)
                self.embedding_available = True
            except Exception as e:
                print(f"✗ 无法加载Embedding模型: {e}")
                self.model = None
                self.embedding_available = False

        self._load()

    def _load(self):
        """加载元数据和FAISS索引"""
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.meta = [json.loads(line) for line in f]
        
        if self.embedding_available and os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                print(f"✓ FAISS索引加载成功，包含 {self.index.ntotal} 个向量ảng。")
            except Exception as e:
                print(f"✗ FAISS索引加载失败: {e}")
                self.index = None
        
        if self.embedding_available and self.index is None:
            # 如果模型可用但索引不存在或加载失败，则初始化一个新索引
            embedding_dim = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(embedding_dim)

    def _save(self):
        """保存元数据和FAISS索引"""
        with open(self.meta_path, "w", encoding="utf-8") as f:
            for m in self.meta:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
        
        if self.embedding_available and self.index:
            faiss.write_index(self.index, self.index_path)

    def add(self, doc_id: str, chunks: List[str]) -> int:
        """将文档块编码为向量并添加到索引中"""
        if not chunks or not self.embedding_available:
            return 0
            
        try:
            # 编码文本块
            embeddings = self.model.encode(chunks, convert_to_tensor=False, show_progress_bar=True)
            
            # 添加到FAISS索引
            self.index.add(np.array(embeddings, dtype='float32'))
            
            # 添加元数据
            base_idx = len(self.meta)
            for i, chunk in enumerate(chunks):
                self.meta.append({
                    "doc_id": doc_id,
                    "chunk_id": i,
                    "text": chunk,
                    "index": base_idx + i
                })
            
            self._save()
            print(f"✓ 成功添加 {len(chunks)} 个文档块到向量存储ảng。")
            return len(chunks)
        except Exception as e:
            print(f"✗ 添加文档到向量存储时出错: {e}")
            return 0

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """对查询进行编码并执行向量搜索"""
        if not self.embedding_available or self.index is None or self.index.ntotal == 0:
            return []
            
        try:
            # 编码查询
            query_vector = self.model.encode([query], convert_to_tensor=False)
            query_vector = np.array(query_vector, dtype='float32')
            
            # FAISS搜索
            distances, indices = self.index.search(query_vector, top_k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.meta):
                    meta_info = self.meta[idx]
                    results.append({
                        "doc_id": meta_info["doc_id"],
                        "chunk_id": meta_info["chunk_id"],
                        "text": meta_info["text"],
                        "score": 1 - distances[0][i] # 转换为相似度分数
                    })
            return results
        except Exception as e:
            print(f"✗ 向量搜索失败: {e}")
            return []

    def get_stats(self) -> Dict:
        """获取存储统计信息"""
        return {
            "total_chunks": len(self.meta),
            "total_docs": len(set(m["doc_id"] for m in self.meta)),
            "storage_type": "vector_store" if self.embedding_available else "simple_text (fallback)",
            "embedding_available": self.embedding_available,
            "index_vectors": self.index.ntotal if self.index else 0
        }
